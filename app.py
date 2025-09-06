"""
Plataforma de Análise de IAs Generativas para Mamografias
Backend FastAPI - Versão corrigida
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import uuid
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from PIL import Image, ImageOps
import io

# Configurações básicas
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = str(BASE_DIR / "uploads")
RESULTS_DIR = str(BASE_DIR / "results")

# Criar diretórios necessários
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Configuração do banco de dados
DATABASE_URL = "sqlite:///./mamografia_analysis.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos do banco de dados
class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=func.now())
    
    # Resultados das análises
    gemini_analysis = Column(Text, nullable=True)
    gpt4v_analysis = Column(Text, nullable=True)
    
    # Metadados
    processing_status = Column(String(50), default="uploaded")
    processing_date = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Campos para futuras funcionalidades
    confidence_score = Column(Float, nullable=True)
    is_processed = Column(Boolean, default=False)

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Dependency para obter sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Criação da instância FastAPI
app = FastAPI(
    title="Plataforma de Análise de IAs Generativas para Mamografias",
    description="API para análise e comparação de mamografias usando diferentes modelos de IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # URLs do frontend Vue.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints básicos
@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Plataforma de Análise de IAs Generativas para Mamografias",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "upload": "/api/v1/upload",
            "analysis": "/api/v1/analyze"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da aplicação"""
    return {
        "status": "healthy", 
        "message": "API funcionando corretamente",
        "directories": {
            "upload": UPLOAD_DIR,
            "results": RESULTS_DIR
        }
    }

# Endpoint de upload com banco de dados
@app.post("/api/v1/upload")
async def upload_mammography(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Endpoint para upload de imagem de mamografia com armazenamento no banco
    """
    try:
        # Verificar se é uma imagem
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
        
        # Verificar extensão
        allowed_extensions = ['.png', '.jpg', '.jpeg']
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Formato não suportado. Use: {', '.join(allowed_extensions)}"
            )
        
        # Ler conteúdo do arquivo
        content = await file.read()

        try:
            image_info = validate_and_process_image(content, file.filename)
        except HTTPException as e:
            raise
        except Exception as e:
            raise HTTPException(status_code=500,
            detail=f"Erro ao processar imagem: {str(e)}")
        
        
        # Verificar tamanho (10MB máximo)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(content) > max_size:
            raise HTTPException(
                status_code=400, 
                detail=f"Arquivo muito grande. Tamanho máximo: {max_size / (1024*1024):.1f}MB"
            )
        
        # Gerar nome único para o arquivo
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Salvar arquivo
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Salvar no banco de dados
        analysis = Analysis(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            processing_status="uploaded"
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return {
            "message": "Upload realizado com sucesso",
            "analysis_id": analysis.id,
            "filename": unique_filename,
            "original_filename": file.filename,
            "info": image_info,
            "file_size": len(content),
            "status": "uploaded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro no upload: {str(e)}")

# Endpoint para listar uploads do banco
@app.get("/api/v1/uploads")
async def list_uploads(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Listar uploads do banco de dados
    """
    try:
        analyses = db.query(Analysis).offset(skip).limit(limit).all()
        
        return {
            "uploads": [
                {
                    "id": analysis.id,
                    "filename": analysis.filename,
                    "original_filename": analysis.original_filename,
                    "file_size": analysis.file_size,
                    "upload_date": analysis.upload_date,
                    "status": analysis.processing_status,
                    "has_gemini": bool(analysis.gemini_analysis),
                    "has_gpt4v": bool(analysis.gpt4v_analysis)
                }
                for analysis in analyses
            ],
            "count": len(analyses)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar uploads: {str(e)}")

# Endpoint para obter detalhes de uma análise
@app.get("/api/v1/analysis/{analysis_id}")
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Obter detalhes de uma análise específica
    """
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Análise não encontrada")
        
        return {
            "id": analysis.id,
            "filename": analysis.filename,
            "original_filename": analysis.original_filename,
            "file_size": analysis.file_size,
            "upload_date": analysis.upload_date,
            "processing_date": analysis.processing_date,
            "status": analysis.processing_status,
            "error_message": analysis.error_message,
            "results": {
                "gemini": analysis.gemini_analysis,
                "gpt4v": analysis.gpt4v_analysis
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao obter análise: {str(e)}")

# Endpoint de análise básico (preparado para IA)
@app.post("/api/v1/analyze/{analysis_id}")
async def analyze_mammography(analysis_id: int, db: Session = Depends(get_db)):
    """
    Endpoint para análise de mamografia (preparado para IA)
    """
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Análise não encontrada")
        
        if not os.path.exists(analysis.file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        # Atualizar status para processando
        analysis.processing_status = "processing"
        analysis.processing_date = datetime.utcnow()
        db.commit()
        
        # Por enquanto, retorna uma análise simulada
        return {
            "message": "Análise iniciada",
            "analysis_id": analysis_id,
            "filename": analysis.filename,
            "status": "processing",
            "note": "Funcionalidade de IA será implementada quando as chaves de API forem configuradas"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na análise: {str(e)}")

def validate_and_process_image(file_content: bytes, filename: str) -> dict:
    """
    Valida e processa imagem de mamografia
    
    Args:
        file_content: Conteúdo binário da imagem
        filename: Nome do arquivo
    
    Returns:
        dict: Informações da imagem processada
    
    Raises:
        HTTPException: Se a imagem for inválida
    """
    try:
        # Abrir imagem
        image = Image.open(io.BytesIO(file_content))

        image.verify()

        # Reabrir para processamento já que verify fecha a imagem
        image = Image.open(io.BytesIO(file_content))

        width, height = image.size

        min_width, min_height = 100, 100
        max_width, max_height = 4000, 4000

        if width < min_width or height < min_height:
            raise HTTPException(
                status_code=400,
                detail=f"Imagem muito pequena. Mínimo de {min_width}x{min_height}px"
            )
        
        if width > max_width or height > max_height:
            raise HTTPException(
                status_code=400,
                detail=f"Imagem muito grande. Máximo de {max_width}x{max_height}px"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo não é uma imagem válida: {str(e)}"
        )

    # Convertar para RGB se necessário
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Otimizações para análise
    image = ImageOps.autocontrast(image)

    max_size = (1024, 1024)
    if width > max_size[0] or height > max_size[1]:
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        width, height = image.size

    return {
        "dimensions": (width, height),
        "format": image.format,
        "mode": image.mode,
        "is_optimized": width <= 1024 and height <= 1024
    }

if __name__ == "__main__":
    print("🚀 Iniciando aplicação FastAPI...")
    print(f"📁 Upload dir: {UPLOAD_DIR}")
    print(f"📁 Results dir: {RESULTS_DIR}")
    print("🌐 Acesse: http://localhost:8000/docs")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
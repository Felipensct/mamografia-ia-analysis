"""
Plataforma de Análise de IAs Generativas para Mamografias
Backend FastAPI - Versão corrigida
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import os
import uuid
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from PIL import Image, ImageOps
import io
import pydicom
from pydicom.errors import InvalidDicomError
import numpy as np
from services.ai_service import AIService

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
    
    # Informações de processamento da imagem
    info = Column(Text, nullable=True)
    
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

# Instância do serviço de IA
ai_service = AIService()

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
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],  # URLs do frontend Vue.js
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

# Endpoint para servir imagens
@app.get("/uploads/{filename}")
@app.head("/uploads/{filename}")
async def get_image(filename: str):
    """
    Endpoint para servir imagens enviadas
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    return FileResponse(file_path, media_type="image/jpeg")

# Endpoint de upload com banco de dados
@app.post("/api/v1/upload")
async def upload_mammography(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Endpoint para upload de imagem de mamografia com armazenamento no banco
    """
    try:
        # Verificar se é uma imagem ou arquivo DICOM
        allowed_content_types = ['image/', 'application/dicom', 'application/octet-stream']
        is_valid_content_type = any(file.content_type.startswith(ct) for ct in allowed_content_types)
        
        if not is_valid_content_type:
            raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem ou arquivo DICOM")
        
        # Verificar extensão
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.dcm']
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Formato não suportado. Use: {', '.join(allowed_extensions)}"
            )
        
        # Ler conteúdo do arquivo
        content = await file.read()

        # Processar arquivo DICOM se necessário
        if file_extension == '.dcm':
            try:
                # Converter DICOM para imagem
                content, dicom_info = convert_dicom_to_image(content, file.filename)
                # Usar informações do DICOM como base
                image_info = {
                    "dimensions": (dicom_info["rows"], dicom_info["columns"]),
                    "format": "DICOM",
                    "mode": "RGB",
                    "is_optimized": True,
                    "was_resized": False,
                    "original_dimensions": None,
                    "dicom_metadata": dicom_info
                }
            except HTTPException as e:
                raise
            except Exception as e:
                raise HTTPException(status_code=500,
                detail=f"Erro ao processar arquivo DICOM: {str(e)}")
        else:
            try:
                image_info = validate_and_process_image(content, file.filename)
            except HTTPException as e:
                raise
            except Exception as e:
                raise HTTPException(status_code=500,
                detail=f"Erro ao processar imagem: {str(e)}")
        
        
        # Verificar tamanho baseado no tipo de arquivo
        is_dicom = file_extension == '.dcm'
        max_size = 50 * 1024 * 1024 if is_dicom else 10 * 1024 * 1024  # 50MB para DICOM, 10MB para outros
        max_size_mb = max_size / (1024*1024)
        
        if len(content) > max_size:
            raise HTTPException(
                status_code=400, 
                detail=f"Arquivo muito grande. Tamanho máximo: {max_size_mb:.0f}MB"
            )
        
        # Gerar nome único para o arquivo
        if file_extension == '.dcm':
            # Para DICOM, salvar como JPEG convertido
            unique_filename = f"{uuid.uuid4()}.jpg"
        else:
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
            processing_status="uploaded",
            info=json.dumps(image_info)
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

# Endpoint para listar todas as análises
@app.get("/api/v1/analyses")
async def list_analyses(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Listar todas as análises do banco de dados
    """
    try:
        analyses = db.query(Analysis).offset(skip).limit(limit).all()
        
        return {
            "analyses": [
                {
                    "id": analysis.id,
                    "filename": analysis.filename,
                    "original_filename": analysis.original_filename,
                    "file_size": analysis.file_size,
                    "upload_date": analysis.upload_date,
                    "processing_date": analysis.processing_date,
                    "status": analysis.processing_status,
                    "is_processed": analysis.is_processed,
                    "has_analysis": bool(analysis.gemini_analysis),
                    "error_message": analysis.error_message
                }
                for analysis in analyses
            ],
            "count": len(analyses)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar análises: {str(e)}")

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
        
        # Parse info from JSON string
        info_data = None
        if analysis.info:
            try:
                info_data = json.loads(analysis.info)
            except:
                info_data = None
        
        return {
            "id": analysis.id,
            "filename": analysis.filename,
            "original_filename": analysis.original_filename,
            "file_size": analysis.file_size,
            "upload_date": analysis.upload_date,
            "processing_date": analysis.processing_date,
            "status": analysis.processing_status,
            "error_message": analysis.error_message,
            "info": info_data,
            "results": {
                "gemini": analysis.gemini_analysis,
                "gpt4v": analysis.gpt4v_analysis
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao obter análise: {str(e)}")

# Endpoint de análise com IA

@app.post("/api/v1/analyze/{analysis_id}")
async def analyze_mammography(analysis_id: int, db: Session = Depends(get_db)):
    """
    Endpoint para análise de mamografia com IA (Gemini)
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
        
        # Fazer análise com Gemini
        gemini_result = ai_service.analyze_mammography(analysis.file_path)
        
        if gemini_result["success"]:
            # Salvar resultado no banco
            analysis.gemini_analysis = gemini_result["analysis"]
            analysis.processing_status = "completed"
            analysis.is_processed = True
            db.commit()
            
            return {
                "message": "Análise concluída com sucesso",
                "analysis_id": analysis_id,
                "filename": analysis.filename,
                "status": "completed",
                "model": gemini_result["model"],
                "analysis": gemini_result["analysis"]
            }
        else:
            # Se Gemini falhar, tentar Hugging Face
            hf_result = ai_service.analyze_with_alternative_api(analysis.file_path)
            
            if hf_result["success"]:
                analysis.gemini_analysis = hf_result["analysis"]
                analysis.processing_status = "completed"
                analysis.is_processed = True
                db.commit()
                
                return {
                    "message": "Análise concluída com Hugging Face",
                    "analysis_id": analysis_id,
                    "filename": analysis.filename,
                    "status": "completed",
                    "model": hf_result["model"],
                    "analysis": hf_result["analysis"]
                }
            else:
                # Se ambos falharem
                analysis.processing_status = "error"
                analysis.error_message = f"Gemini: {gemini_result['error']} | HF: {hf_result['error']}"
                db.commit()
                
                raise HTTPException(
                    status_code=500, 
                    detail=f"Erro na análise: {gemini_result['error']}"
                )
        
    except HTTPException:
        raise
    except Exception as e:
        # Atualizar status de erro
        analysis.processing_status = "error"
        analysis.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

# Endpoint alternativo para Hugging Face
@app.post("/api/v1/analyze-huggingface/{analysis_id}")
async def analyze_mammography_hf(analysis_id: int, db: Session = Depends(get_db)):
    """
    Endpoint para análise de mamografia com Hugging Face
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
        
        # Fazer análise com Hugging Face
        hf_result = ai_service.analyze_with_alternative_api(analysis.file_path)
        
        if hf_result["success"]:
            # Salvar resultado no banco
            analysis.gemini_analysis = hf_result["analysis"]  # Usando o mesmo campo por simplicidade
            analysis.processing_status = "completed"
            analysis.is_processed = True
            db.commit()
            
            return {
                "message": "Análise concluída com Hugging Face",
                "analysis_id": analysis_id,
                "filename": analysis.filename,
                "status": "completed",
                "model": hf_result["model"],
                "analysis": hf_result["analysis"]
            }
        else:
            analysis.processing_status = "error"
            analysis.error_message = hf_result["error"]
            db.commit()
            
            raise HTTPException(
                status_code=500, 
                detail=f"Erro na análise: {hf_result['error']}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        analysis.processing_status = "error"
        analysis.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

# Endpoint para excluir análise
@app.delete("/api/v1/analysis/{analysis_id}")
async def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Excluir análise e arquivo associado
    """
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Análise não encontrada")
        
        # Excluir arquivo físico se existir
        if os.path.exists(analysis.file_path):
            try:
                os.remove(analysis.file_path)
                print(f"🗑️  Arquivo excluído: {analysis.file_path}")
            except Exception as e:
                print(f"⚠️  Erro ao excluir arquivo: {str(e)}")
        
        # Excluir do banco de dados
        db.delete(analysis)
        db.commit()
        
        return {
            "message": "Análise excluída com sucesso",
            "analysis_id": analysis_id,
            "filename": analysis.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao excluir análise: {str(e)}")

def convert_dicom_to_image(file_content: bytes, filename: str) -> tuple[bytes, dict]:
    """
    Converte arquivo DICOM para formato de imagem suportado
    
    Args:
        file_content: Conteúdo binário do arquivo DICOM
        filename: Nome do arquivo original
    
    Returns:
        tuple: (conteúdo da imagem convertida, informações do DICOM)
    
    Raises:
        HTTPException: Se o arquivo DICOM for inválido
    """
    try:
        # Carregar arquivo DICOM (usar force=True para arquivos sem cabeçalho completo)
        dicom_file = pydicom.dcmread(io.BytesIO(file_content), force=True)
        
        # Extrair metadados importantes
        dicom_info = {
            "patient_id": str(dicom_file.get("PatientID", "N/A")),
            "study_date": str(dicom_file.get("StudyDate", "N/A")),
            "study_time": str(dicom_file.get("StudyTime", "N/A")),
            "modality": str(dicom_file.get("Modality", "N/A")),
            "body_part": str(dicom_file.get("BodyPartExamined", "N/A")),
            "study_description": str(dicom_file.get("StudyDescription", "N/A")),
            "series_description": str(dicom_file.get("SeriesDescription", "N/A")),
            "manufacturer": str(dicom_file.get("Manufacturer", "N/A")),
            "manufacturer_model": str(dicom_file.get("ManufacturerModelName", "N/A")),
            "rows": int(dicom_file.get("Rows", 0)),
            "columns": int(dicom_file.get("Columns", 0)),
            "bits_allocated": int(dicom_file.get("BitsAllocated", 16)),
            "photometric_interpretation": str(dicom_file.get("PhotometricInterpretation", "N/A")),
            "window_center": str(dicom_file.get("WindowCenter", "N/A")),
            "window_width": str(dicom_file.get("WindowWidth", "N/A"))
        }
        
        # Obter pixel array
        pixel_array = dicom_file.pixel_array
        
        # Aplicar windowing se disponível
        if hasattr(dicom_file, 'WindowCenter') and hasattr(dicom_file, 'WindowWidth'):
            try:
                window_center = float(dicom_file.WindowCenter)
                window_width = float(dicom_file.WindowWidth)
                
                # Aplicar windowing
                min_val = window_center - window_width / 2
                max_val = window_center + window_width / 2
                
                pixel_array = np.clip(pixel_array, min_val, max_val)
                pixel_array = ((pixel_array - min_val) / (max_val - min_val) * 255).astype(np.uint8)
            except:
                # Se windowing falhar, normalizar diretamente
                pixel_array = ((pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)
        else:
            # Normalizar para 0-255
            pixel_array = ((pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)
        
        # Converter para PIL Image
        if len(pixel_array.shape) == 3:
            # Imagem colorida
            image = Image.fromarray(pixel_array)
        else:
            # Imagem em escala de cinza
            image = Image.fromarray(pixel_array, mode='L')
        
        # Converter para RGB se necessário
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Salvar como JPEG em memória
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG', quality=95)
        img_content = img_buffer.getvalue()
        
        print(f"✅ DICOM convertido com sucesso: {dicom_info['rows']}x{dicom_info['columns']}px")
        print(f"📋 Modalidade: {dicom_info['modality']}, Parte do corpo: {dicom_info['body_part']}")
        
        return img_content, dicom_info
        
    except InvalidDicomError:
        raise HTTPException(
            status_code=400,
            detail="Arquivo DICOM inválido ou corrompido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao processar arquivo DICOM: {str(e)}"
        )

def validate_and_process_image(file_content: bytes, filename: str) -> dict:
    """
                                image.png    Valida e processa imagem de mamografia com redimensionamento inteligente
    
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

        original_width, original_height = image.size

        min_width, min_height = 100, 100
        max_width, max_height = 4000, 4000

        # Verificar tamanho mínimo
        if original_width < min_width or original_height < min_height:
            raise HTTPException(
                status_code=400,
                detail=f"Imagem muito pequena. Mínimo de {min_width}x{min_height}px"
            )
        
        # Se imagem for muito grande, redimensionar automaticamente
        was_resized = False
        if original_width > max_width or original_height > max_height:
            print(f"📏 Imagem grande detectada: {original_width}x{original_height}px")
            print(f"🔄 Redimensionando automaticamente para máximo {max_width}x{max_height}px...")
            
            # Calcular nova dimensão mantendo proporção
            ratio = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            
            print(f"📐 Nova dimensão: {new_width}x{new_height}px (proporção: {ratio:.2f})")
            
            # Redimensionar com alta qualidade
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            was_resized = True
        
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
    
    # Ajustar brilho e contraste para melhor análise
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)  # Aumentar contraste em 20%
    
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.1)  # Aumentar brilho em 10%

    # Resolução otimizada para análise de IA
    final_max_size = (2048, 2048)  # Tamanho ideal para IA
    current_width, current_height = image.size
    
    if current_width > final_max_size[0] or current_height > final_max_size[1]:
        print(f"🎯 Otimizando para análise de IA: {current_width}x{current_height}px → {final_max_size[0]}x{final_max_size[1]}px")
        image.thumbnail(final_max_size, Image.Resampling.LANCZOS)
        current_width, current_height = image.size
        was_resized = True

    # Informações da imagem processada
    processed_info = {
        "dimensions": (current_width, current_height),
        "format": image.format,
        "mode": image.mode,
        "is_optimized": current_width <= 1024 and current_height <= 1024,
        "was_resized": was_resized,
        "original_dimensions": (original_width, original_height) if was_resized else None
    }
    
    if was_resized:
        print(f"✅ Imagem processada: {original_width}x{original_height}px → {current_width}x{current_height}px")
    
    return processed_info

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
        log_level="info",
        timeout_keep_alive=30,
        limit_max_requests=1000
    )
"""
Plataforma de Análise de IAs Generativas para Mamografias
Backend FastAPI - Versão corrigida com suporte a PGM
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
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
from PIL import Image, ImageOps, ImageEnhance
import pydicom
import io
from pydicom.errors import InvalidDicomError
import numpy as np
import hashlib
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
    
    # Metadados
    processing_status = Column(String(50), default="uploaded")
    processing_date = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Informações de processamento da imagem
    info = Column(Text, nullable=True)
    
    # Cache de resultados baseado em hash da imagem
    image_hash = Column(String(32), nullable=True, index=True)
    
    # Campos para futuras funcionalidades
    confidence_score = Column(Float, nullable=True)
    is_processed = Column(Boolean, default=False)

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Executar migração automática se necessário
def run_auto_migration():
    """Executa migração automática do banco de dados"""
    try:
        import sqlite3
        from pathlib import Path
        
        db_path = Path(__file__).parent / "mamografia_analysis.db"
        if not db_path.exists():
            return  # Banco será criado automaticamente pelo SQLAlchemy
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Verificar colunas existentes
        cursor.execute("PRAGMA table_info(analyses)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Adicionar image_hash se não existir
        if 'image_hash' not in columns:
            try:
                cursor.execute("ALTER TABLE analyses ADD COLUMN image_hash VARCHAR(32)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_image_hash ON analyses(image_hash)")
                conn.commit()
                print("✅ Migração automática: coluna 'image_hash' adicionada")
            except Exception as e:
                print(f"⚠️  Aviso na migração automática: {str(e)}")
        
        conn.close()
    except Exception as e:
        print(f"⚠️  Erro na migração automática (não crítico): {str(e)}")

# Executar migração automática
run_auto_migration()

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
    Converte PGM automaticamente para JPEG para compatibilidade com navegadores
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    # Determinar o media_type (content type) baseado na extensão do arquivo
    extension = Path(filename).suffix.lower()
    
    # Se for PGM, converter para JPEG em memória para exibição
    if extension == '.pgm':
        try:
            # Carregar imagem PGM
            with Image.open(file_path) as img:
                # Converter para RGB se necessário
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Salvar como JPEG em memória
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='JPEG', quality=95, optimize=False)
                img_buffer.seek(0)
                
                # Retornar JPEG convertido
                return Response(
                    content=img_buffer.getvalue(),
                    media_type='image/jpeg',
                    headers={
                        'Content-Disposition': f'inline; filename="{Path(filename).stem}.jpg"'
                    }
                )
        except Exception as e:
            print(f"Erro ao converter PGM para JPEG: {str(e)}")
            # Fallback: retornar arquivo original
            return FileResponse(file_path, media_type='image/x-portable-graymap')
    
    # Para outros formatos, retornar normalmente
    media_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.dcm': 'application/dicom'
    }
    media_type = media_type_map.get(extension, 'application/octet-stream')
    
    return FileResponse(file_path, media_type=media_type)

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
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.dcm', '.pgm']
        file_extension = Path(file.filename).suffix.lower()
        
        # Permite se for um tipo 'image/' ou se for .pgm ou .dcm
        is_image_type = file.content_type and file.content_type.startswith('image/')
        is_special_format = file_extension in ['.pgm', '.dcm']
        
        if not (is_image_type or is_special_format):
            raise HTTPException(
                status_code=400, 
                detail=f"Arquivo deve ser uma imagem válida ({', '.join(allowed_extensions)})"
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
        
        # Calcular hash MD5 do conteúdo para cache
        image_hash = hashlib.md5(content).hexdigest()
        
        # Verificar se já existe análise com mesmo hash (cache)
        existing_analysis = db.query(Analysis).filter(Analysis.image_hash == image_hash).first()
        if existing_analysis and existing_analysis.gemini_analysis:
            # Retornar análise existente do cache
            return {
                "message": "Upload realizado com sucesso (análise do cache)",
                "analysis_id": existing_analysis.id,
                "filename": existing_analysis.filename,
                "original_filename": file.filename,
                "info": json.loads(existing_analysis.info) if existing_analysis.info else image_info,
                "file_size": len(content),
                "status": "uploaded",
                "from_cache": True
            }
        
        # Gerar nome único para o arquivo
        if file_extension == '.dcm':
            # Para DICOM, salvar como JPEG convertido
            unique_filename = f"{uuid.uuid4()}.jpg"
        else:
            unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Salvar arquivo original no disco
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Salvar no banco de dados
        analysis = Analysis(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            processing_status="uploaded",
            info=json.dumps(image_info),
            image_hash=image_hash
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
                    "upload_date": analysis.upload_date.isoformat() if analysis.upload_date else None,
                    "status": analysis.processing_status,
                    "has_gemini": bool(analysis.gemini_analysis)
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
                    "upload_date": analysis.upload_date.isoformat() if analysis.upload_date else None,
                    "processing_date": analysis.processing_date.isoformat() if analysis.processing_date else None,
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
            "upload_date": analysis.upload_date.isoformat() if analysis.upload_date else None,
            "processing_date": analysis.processing_date.isoformat() if analysis.processing_date else None,
            "status": analysis.processing_status,
            "error_message": analysis.error_message,
            "info": info_data,
            "results": {
                "gemini": analysis.gemini_analysis
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao obter análise: {str(e)}")

# Endpoint de análise com IA
@app.post("/api/v1/analyze/{analysis_id}")
async def analyze_mammography(analysis_id: int, db: Session = Depends(get_db)):
    """
    Endpoint para análise de mamografia com IA (Gemini)
    Verifica cache baseado em hash da imagem antes de processar
    """
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Análise não encontrada")
        
        if not os.path.exists(analysis.file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        # Se já tem resultado, retornar sem reprocessar
        if analysis.gemini_analysis:
            return {
                "message": "Análise já existe",
                "analysis_id": analysis_id,
                "filename": analysis.filename,
                "status": "completed",
                "model": "Gemini 2.5 Pro",
                "analysis": analysis.gemini_analysis
            }
        
        # Verificar cache ANTES de processar (mesmo hash, resultado existente)
        if analysis.image_hash:
            # Buscar análise com mesmo hash que já tenha resultado
            cached_analysis = db.query(Analysis).filter(
                Analysis.image_hash == analysis.image_hash,
                Analysis.gemini_analysis.isnot(None),
                Analysis.id != analysis_id
            ).first()
            
            if cached_analysis:
                # Copiar resultado do cache
                analysis.gemini_analysis = cached_analysis.gemini_analysis
                analysis.processing_status = "completed"
                analysis.is_processed = True
                analysis.processing_date = datetime.utcnow()
                db.commit()
                
                print(f"✅ Cache encontrado! Reutilizando resultado da análise ID {cached_analysis.id}")
                
                return {
                    "message": "Análise concluída com sucesso (do cache)",
                    "analysis_id": analysis_id,
                    "filename": analysis.filename,
                    "status": "completed",
                    "model": "Gemini 2.5 Pro (cached)",
                    "analysis": analysis.gemini_analysis,
                    "from_cache": True
                }
        
        # Atualizar status para processando
        analysis.processing_status = "processing"
        analysis.processing_date = datetime.utcnow()
        db.commit()
        
        # Gerar image_id baseado no nome original do arquivo ou hash da imagem
        # Isso garante que a mesma imagem sempre tenha o mesmo image_id
        image_id = None
        if analysis.original_filename:
            # Tentar extrair ID do nome original (ex: mdb001.pgm -> mdb001)
            original_name = Path(analysis.original_filename).stem
            # Verificar se segue padrão MIAS (mdb###)
            if original_name.lower().startswith('mdb') and len(original_name) >= 6:
                image_id = original_name.lower()[:6]  # mdb001, mdb002, etc.
        
        # Se não conseguiu extrair do nome, usar hash da imagem
        if not image_id and analysis.image_hash:
            image_id = f"mdb_{analysis.image_hash[:8]}"
        
        # Fallback: usar ID do banco (menos ideal, mas funciona)
        if not image_id:
            image_id = f"mdb{analysis.id:03d}"
        
        print(f"🆔 Image ID gerado: {image_id} (original: {analysis.original_filename}, hash: {analysis.image_hash[:8] if analysis.image_hash else 'N/A'})")
        
        gemini_result = ai_service.analyze_mammography(analysis.file_path, image_id=image_id)
        
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
            # Se Gemini falhar, tentar Hugging Face (ou outro modelo)
            hf_result = ai_service.analyze_with_alternative_api(analysis.file_path)
            
            if hf_result["success"]:
                analysis.gemini_analysis = hf_result["analysis"] # Salva no mesmo campo (pode ser ajustado)
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
                    detail=f"Erro na análise: {analysis.error_message}"
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
            analysis.gemini_analysis = hf_result["analysis"]  # Usando o campo principal por simplicidade
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
        
        # Aplicar windowing se disponível (processamento determinístico)
        if hasattr(dicom_file, 'WindowCenter') and hasattr(dicom_file, 'WindowWidth'):
            try:
                # Garantir que WindowCenter e WindowWidth sejam valores únicos (não listas)
                window_center = dicom_file.WindowCenter
                window_width = dicom_file.WindowWidth
                
                if isinstance(window_center, (list, tuple)):
                    window_center = float(window_center[0])
                else:
                    window_center = float(window_center)
                
                if isinstance(window_width, (list, tuple)):
                    window_width = float(window_width[0])
                else:
                    window_width = float(window_width)
                
                # Aplicar windowing de forma consistente
                min_val = window_center - window_width / 2
                max_val = window_center + window_width / 2
                
                pixel_array = np.clip(pixel_array, min_val, max_val)
                # Normalizar para 0-255 de forma determinística
                pixel_min = pixel_array.min()
                pixel_max = pixel_array.max()
                if pixel_max > pixel_min:
                    pixel_array = ((pixel_array - pixel_min) / (pixel_max - pixel_min) * 255).astype(np.uint8)
                else:
                    pixel_array = np.zeros_like(pixel_array, dtype=np.uint8)
            except Exception as e:
                print(f"⚠️  Erro no windowing DICOM, usando normalização padrão: {str(e)}")
                # Se windowing falhar, normalizar diretamente de forma determinística
                pixel_min = pixel_array.min()
                pixel_max = pixel_array.max()
                if pixel_max > pixel_min:
                    pixel_array = ((pixel_array - pixel_min) / (pixel_max - pixel_min) * 255).astype(np.uint8)
                else:
                    pixel_array = np.zeros_like(pixel_array, dtype=np.uint8)
        else:
            # Normalizar para 0-255 de forma determinística
            pixel_min = pixel_array.min()
            pixel_max = pixel_array.max()
            if pixel_max > pixel_min:
                pixel_array = ((pixel_array - pixel_min) / (pixel_max - pixel_min) * 255).astype(np.uint8)
            else:
                pixel_array = np.zeros_like(pixel_array, dtype=np.uint8)
        
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
        
        # Salvar como JPEG em memória (qualidade fixa para consistência)
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG', quality=95, optimize=False)  # optimize=False para consistência
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
    Valida e processa imagem de mamografia com redimensionamento e otimização.
    """
    try:
        # Tratamento especial para arquivos DICOM
        if filename.lower().endswith('.dcm'):
            print("🏥 Processando arquivo DICOM...")
            # Ler arquivo DICOM da memória
            dataset = pydicom.dcmread(io.BytesIO(file_content))
            
            # Converter para array e normalizar (processamento determinístico)
            pixel_array = dataset.pixel_array
            
            # Normalizar para 0-255 de forma consistente
            pixel_min = pixel_array.min()
            pixel_max = pixel_array.max()
            if pixel_max > pixel_min:
                normalized_image = ((pixel_array - pixel_min) / 
                                 (pixel_max - pixel_min) * 255).astype('uint8')
            else:
                normalized_image = np.zeros_like(pixel_array, dtype=np.uint8)
            
            # Converter para imagem PIL
            image = Image.fromarray(normalized_image)
            
            # Converter para RGB
            image = image.convert('RGB')
            print("🎨 Convertido DICOM para RGB")
            
            original_width, original_height = image.size
        else:
            # Processamento normal para outros tipos de imagem
            image = Image.open(io.BytesIO(file_content))
            original_width, original_height = image.size
        
        # Tratamento especial para PGM
        if filename.lower().endswith('.pgm'):
            print(f"🖼️ Processando imagem PGM: modo={image.mode}")
            # Converter para RGB mantendo informações da escala de cinza
            if image.mode in ['L', 'I']:
                image = image.convert('RGB')
                print("🎨 Convertido PGM para RGB")

        # Verificar tamanho mínimo
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
            detail=f"Erro ao processar imagem: {str(e)}"
        )

    # 🚨 CORREÇÃO PGM: Converte para RGB se necessário (inclui imagens PGM que são L ou I)
    if image.mode != "RGB":
        print(f"🎨 Convertendo imagem de {image.mode} para RGB para consistência com modelos de IA...")
        image = image.convert("RGB")

    # Otimizações para análise
    image = ImageOps.autocontrast(image)
    
    # Ajustar brilho e contraste para melhor análise
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
        # Aqui, 2048x2048 é o limite ideal para IA (não 1024)
        "is_optimized": current_width <= final_max_size[0] and current_height <= final_max_size[1],
        "was_resized": was_resized,
        "original_dimensions": (original_width, original_height)
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
"""
Plataforma de Análise de IAs Generativas para Mamografias
Backend FastAPI - Versão corrigida
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from pathlib import Path

# Configurações básicas
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = str(BASE_DIR / "uploads")
RESULTS_DIR = str(BASE_DIR / "results")

# Criar diretórios necessários
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

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

# Endpoint de upload básico
@app.post("/api/v1/upload")
async def upload_mammography(file: UploadFile = File(...)):
    """
    Endpoint básico para upload de imagem de mamografia
    """
    try:
        # Verificar se é uma imagem
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
        
        # Ler conteúdo do arquivo
        content = await file.read()
        
        # Salvar arquivo
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        return {
            "message": "Upload realizado com sucesso",
            "filename": file.filename,
            "file_size": len(content),
            "file_path": file_path,
            "status": "uploaded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro no upload: {str(e)}")

# Endpoint para listar uploads
@app.get("/api/v1/uploads")
async def list_uploads():
    """
    Listar arquivos enviados
    """
    try:
        files = []
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    files.append({
                        "filename": filename,
                        "size": stat.st_size,
                        "upload_time": stat.st_mtime
                    })
        
        return {
            "uploads": files,
            "count": len(files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar uploads: {str(e)}")

# Endpoint de análise básico
@app.post("/api/v1/analyze/{filename}")
async def analyze_mammography(filename: str):
    """
    Endpoint básico para análise de mamografia
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        # Por enquanto, retorna uma análise simulada
        return {
            "message": "Análise iniciada",
            "filename": filename,
            "status": "processing",
            "note": "Funcionalidade de IA será implementada quando as chaves de API forem configuradas"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na análise: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando aplicação FastAPI...")
    print(f"📁 Upload dir: {UPLOAD_DIR}")
    print(f"📁 Results dir: {RESULTS_DIR}")
    print("🌐 Acesse: http://localhost:8000/docs")
    
    uvicorn.run(
        "main_fixed:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
#!/bin/bash

# Script para instalar dependências via pacotes do sistema Ubuntu/Debian

echo "🚀 Instalando dependências via pacotes do sistema..."

# Atualizar lista de pacotes
echo "📦 Atualizando lista de pacotes..."
sudo apt update

# Instalar pacotes Python essenciais
echo "🐍 Instalando pacotes Python..."
sudo apt install -y python3-full python3-pip python3-venv

# Instalar dependências do projeto via apt
echo "📚 Instalando dependências do projeto..."

# FastAPI e Uvicorn
sudo apt install -y python3-fastapi python3-uvicorn

# Pillow para processamento de imagens
sudo apt install -y python3-pil python3-pil.imagetk

# SQLAlchemy para banco de dados
sudo apt install -y python3-sqlalchemy

# Pydantic para validação
sudo apt install -y python3-pydantic

# Outras dependências
sudo apt install -y python3-multipart python3-dotenv

# Instalar pacotes que não estão disponíveis via apt usando pip com --break-system-packages
echo "🔧 Instalando pacotes adicionais via pip..."

# APIs de IA (não disponíveis via apt)
pip3 install google-generativeai openai --break-system-packages

echo "✅ Instalação concluída!"
echo ""
echo "🧪 Testando instalação..."
python3 -c "
try:
    import fastapi
    print('✅ FastAPI - OK')
except ImportError:
    print('❌ FastAPI - FALHOU')

try:
    import uvicorn
    print('✅ Uvicorn - OK')
except ImportError:
    print('❌ Uvicorn - FALHOU')

try:
    from PIL import Image
    print('✅ Pillow - OK')
except ImportError:
    print('❌ Pillow - FALHOU')

try:
    import sqlalchemy
    print('✅ SQLAlchemy - OK')
except ImportError:
    print('❌ SQLAlchemy - FALHOU')

try:
    import pydantic
    print('✅ Pydantic - OK')
except ImportError:
    print('❌ Pydantic - FALHOU')
"

echo ""
echo "🎉 Instalação finalizada!"
echo "📋 Próximos passos:"
echo "1. Execute: python3 run.py"
echo "2. Acesse: http://localhost:8000/docs"
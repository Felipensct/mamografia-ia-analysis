#!/bin/bash

# Script para reconstruir o ambiente virtual
# Use quando houver problemas com dependências

set -e

echo "🔄 Reconstruindo Ambiente Virtual Python"
echo "========================================"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Diretório do backend
BACKEND_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$BACKEND_DIR"

# Remover ambiente virtual antigo
if [ -d "venv" ]; then
    echo -e "${YELLOW}🗑️  Removendo ambiente virtual antigo...${NC}"
    rm -rf venv
    echo -e "${GREEN}✅ Ambiente removido${NC}"
    echo ""
fi

# Criar novo ambiente virtual
echo -e "${BLUE}📦 Criando novo ambiente virtual...${NC}"
python3 -m venv venv
echo -e "${GREEN}✅ Ambiente criado${NC}"
echo ""

# Ativar ambiente
echo -e "${BLUE}🔧 Ativando ambiente...${NC}"
source venv/bin/activate
echo -e "${GREEN}✅ Ambiente ativado${NC}"
echo ""

# Atualizar pip, setuptools e wheel
echo -e "${BLUE}⬆️  Atualizando ferramentas base...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✅ Ferramentas atualizadas${NC}"
echo ""

# Instalar dependências
echo -e "${BLUE}📦 Instalando dependências...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependências instaladas${NC}"
echo ""

# Verificar instalação
echo -e "${BLUE}✓ Verificando instalação...${NC}"
python3 -c "import cv2; import numpy; import fastapi; print('✅ Pacotes principais OK')"
echo ""

echo -e "${GREEN}🎉 Ambiente virtual reconstruído com sucesso!${NC}"
echo ""
echo -e "${BLUE}Para usar:${NC}"
echo "  cd Backend"
echo "  source venv/bin/activate"
echo "  python3 app.py"
echo ""


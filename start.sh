#!/bin/bash

# Script de inicialização rápida - Mamografia IA
# Univap - Projetos IV - 2025

set -e

echo "🏥 Plataforma de Análise de Mamografias com IA"
echo "================================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretório raiz do projeto
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$PROJECT_DIR/Backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Verificar se está no diretório correto
if [ ! -d "$BACKEND_DIR" ] || [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Erro: Diretórios do projeto não encontrados!${NC}"
    exit 1
fi

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar dependências
echo -e "${BLUE}🔍 Verificando dependências...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 não encontrado!${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ Node.js/npm não encontrado!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependências OK${NC}"
echo ""

# Verificar arquivo .env do backend
echo -e "${BLUE}🔧 Verificando configuração...${NC}"

if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado no Backend${NC}"
    if [ -f "$BACKEND_DIR/env.example" ]; then
        cp "$BACKEND_DIR/env.example" "$BACKEND_DIR/.env"
        echo -e "${GREEN}✅ Arquivo .env criado a partir do env.example${NC}"
        echo -e "${RED}⚠️  IMPORTANTE: Configure suas chaves de API em Backend/.env${NC}"
        echo -e "${YELLOW}   Edite o arquivo e adicione:${NC}"
        echo -e "${YELLOW}   - GEMINI_API_KEY=sua_chave_aqui${NC}"
        echo -e "${YELLOW}   - HUGGINGFACE_API_KEY=sua_chave_aqui${NC}"
        read -p "Pressione ENTER após configurar as chaves de API..."
    fi
fi

# Verificar se as chaves estão configuradas
if grep -q "your_gemini_api_key_here" "$BACKEND_DIR/.env" 2>/dev/null; then
    echo -e "${RED}⚠️  AVISO: Chaves de API não configuradas!${NC}"
    echo -e "${YELLOW}   Edite Backend/.env e adicione suas chaves${NC}"
    read -p "Continuar mesmo assim? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""

# Verificar se precisa instalar dependências do backend
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo -e "${BLUE}📦 Criando ambiente virtual Python...${NC}"
    cd "$BACKEND_DIR"
    python3 -m venv venv
    echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
fi

# Ativar ambiente virtual e instalar dependências
echo -e "${BLUE}📦 Instalando dependências do Backend...${NC}"
cd "$BACKEND_DIR"
source venv/bin/activate

# Atualizar pip, setuptools e wheel
pip install -q --upgrade pip setuptools wheel

# Tentar instalar dependências
if ! pip install -q -r requirements.txt 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Problema na instalação, recriando ambiente virtual...${NC}"
    deactivate
    rm -rf venv
    python3 -m venv venv
    source venv/bin/activate
    pip install -q --upgrade pip setuptools wheel
    pip install -r requirements.txt
fi

echo -e "${GREEN}✅ Dependências do Backend instaladas${NC}"
echo ""

# Verificar se precisa instalar dependências do frontend
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${BLUE}📦 Instalando dependências do Frontend...${NC}"
    cd "$FRONTEND_DIR"
    npm install --silent
    echo -e "${GREEN}✅ Dependências do Frontend instaladas${NC}"
    echo ""
fi

# Verificar migração do banco de dados
if [ -f "$BACKEND_DIR/mamografia_analysis.db" ]; then
    echo -e "${BLUE}🔄 Verificando migração do banco de dados...${NC}"
    cd "$BACKEND_DIR"
    python3 migrate_database.py status
    
    # Executar migração se necessário
    if ! python3 migrate_database.py > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Executando migração automática...${NC}"
        python3 migrate_database.py
    fi
    echo ""
fi

# Perguntar qual modo de execução
echo -e "${BLUE}🚀 Escolha o modo de execução:${NC}"
echo ""
echo "  1) Terminal único (Backend + Frontend em background)"
echo "  2) Terminais separados (recomendado para desenvolvimento)"
echo "  3) Apenas Backend"
echo "  4) Apenas Frontend"
echo ""
read -p "Escolha uma opção (1-4): " exec_choice

case $exec_choice in
    1)
        echo -e "${BLUE}🚀 Iniciando Backend e Frontend...${NC}"
        
        # Iniciar Backend em background
        cd "$BACKEND_DIR"
        source venv/bin/activate
        python3 app.py > /tmp/mamografia-backend.log 2>&1 &
        BACKEND_PID=$!
        
        # Aguardar backend iniciar
        sleep 3
        
        # Verificar se backend iniciou
        if ps -p $BACKEND_PID > /dev/null; then
            echo -e "${GREEN}✅ Backend iniciado (PID: $BACKEND_PID)${NC}"
        else
            echo -e "${RED}❌ Erro ao iniciar Backend${NC}"
            cat /tmp/mamografia-backend.log
            exit 1
        fi
        
        # Iniciar Frontend em background
        cd "$FRONTEND_DIR"
        npm run dev > /tmp/mamografia-frontend.log 2>&1 &
        FRONTEND_PID=$!
        
        # Aguardar frontend iniciar
        sleep 5
        
        # Verificar se frontend iniciou
        if ps -p $FRONTEND_PID > /dev/null; then
            echo -e "${GREEN}✅ Frontend iniciado (PID: $FRONTEND_PID)${NC}"
        else
            echo -e "${RED}❌ Erro ao iniciar Frontend${NC}"
            cat /tmp/mamografia-frontend.log
            kill $BACKEND_PID 2>/dev/null
            exit 1
        fi
        
        echo ""
        echo -e "${GREEN}🎉 Aplicação iniciada com sucesso!${NC}"
        echo ""
        echo -e "${BLUE}📱 Acessos:${NC}"
        echo -e "   Frontend: ${GREEN}http://localhost:5173${NC}"
        echo -e "   API Docs: ${GREEN}http://localhost:8000/docs${NC}"
        echo -e "   Health:   ${GREEN}http://localhost:8000/health${NC}"
        echo ""
        echo -e "${YELLOW}📋 PIDs:${NC}"
        echo -e "   Backend:  $BACKEND_PID"
        echo -e "   Frontend: $FRONTEND_PID"
        echo ""
        echo -e "${BLUE}📝 Logs:${NC}"
        echo -e "   Backend:  tail -f /tmp/mamografia-backend.log"
        echo -e "   Frontend: tail -f /tmp/mamografia-frontend.log"
        echo ""
        echo -e "${RED}⚠️  Para parar os serviços:${NC}"
        echo -e "   kill $BACKEND_PID $FRONTEND_PID"
        echo -e "   ou execute: ${YELLOW}./stop.sh${NC}"
        echo ""
        
        # Criar script de parada
        cat > "$PROJECT_DIR/stop.sh" <<EOF
#!/bin/bash
echo "Parando serviços..."
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
echo "Serviços parados!"
EOF
        chmod +x "$PROJECT_DIR/stop.sh"
        
        # Aguardar Ctrl+C
        echo "Pressione Ctrl+C para ver os logs em tempo real"
        sleep 2
        tail -f /tmp/mamografia-backend.log /tmp/mamografia-frontend.log
        ;;
        
    2)
        echo -e "${BLUE}🚀 Prepare dois terminais:${NC}"
        echo ""
        echo -e "${GREEN}Terminal 1 - Backend:${NC}"
        echo "  cd $BACKEND_DIR"
        echo "  source venv/bin/activate"
        echo "  python3 app.py"
        echo ""
        echo -e "${GREEN}Terminal 2 - Frontend:${NC}"
        echo "  cd $FRONTEND_DIR"
        echo "  npm run dev"
        echo ""
        ;;
        
    3)
        echo -e "${BLUE}🚀 Iniciando apenas Backend...${NC}"
        cd "$BACKEND_DIR"
        source venv/bin/activate
        python3 app.py
        ;;
        
    4)
        echo -e "${BLUE}🚀 Iniciando apenas Frontend...${NC}"
        cd "$FRONTEND_DIR"
        npm run dev
        ;;
        
    *)
        echo -e "${RED}❌ Opção inválida${NC}"
        exit 1
        ;;
esac


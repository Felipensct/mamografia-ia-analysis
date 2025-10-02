#!/bin/bash

# =============================================================================
# Instalação Rápida - Projeto Mamografia IA Analysis
# Rocky Linux / RHEL / CentOS / AlmaLinux
# =============================================================================

set -e

echo "🚀 Instalação Rápida - Mamografia IA Analysis"
echo "=============================================="

# Verificar se é root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Não execute como root. Execute como usuário normal."
    exit 1
fi

# Atualizar sistema
echo "📦 Atualizando sistema..."
sudo dnf update -y

# Instalar dependências básicas
echo "📦 Instalando dependências..."
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y python3 python3-pip python3-devel nodejs npm git curl

# Instalar Python packages
echo "🐍 Instalando dependências Python..."
pip3 install --user fastapi uvicorn python-multipart pillow sqlalchemy python-dotenv google-generativeai requests

# Instalar Node.js packages (globalmente para simplicidade)
echo "📦 Instalando dependências Node.js..."
sudo npm install -g @vue/cli

# Criar diretório do projeto
echo "📁 Criando diretório do projeto..."
mkdir -p ~/mamografia-ia-analysis
cd ~/mamografia-ia-analysis

# Clonar repositório
echo "📥 Clonando repositório..."
if [ -d "Backend" ]; then
    echo "Repositório já existe, atualizando..."
    git pull
else
    git clone https://github.com/Felipensct/mamografia-ia-analysis.git .
fi

# Configurar backend
echo "🔧 Configurando backend..."
cd Backend

# Criar .env se não existir
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "⚠️  Configure suas chaves de API em: ~/mamografia-ia-analysis/Backend/.env"
fi

# Criar diretórios
mkdir -p uploads results

# Configurar frontend
echo "🎨 Configurando frontend..."
cd ../frontend

# Instalar dependências
npm install

# Build de produção
echo "🏗️  Fazendo build de produção..."
npm run build

# Voltar ao diretório raiz
cd ..

# Criar script de execução
echo "📝 Criando script de execução..."
cat > run.sh << 'EOF'
#!/bin/bash

echo "🚀 Iniciando Projeto Mamografia IA Analysis"
echo "==========================================="

# Função para matar processos nas portas
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo "🔄 Parando processo na porta $port (PID: $pid)"
        kill -9 $pid
    fi
}

# Parar processos existentes
kill_port 8000
kill_port 5173

# Iniciar backend
echo "🔧 Iniciando backend..."
cd Backend
python3 app.py &
BACKEND_PID=$!

# Aguardar backend iniciar
sleep 3

# Iniciar frontend (modo desenvolvimento)
echo "🎨 Iniciando frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Serviços iniciados!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 Docs:     http://localhost:8000/docs"
echo ""
echo "Para parar os serviços, pressione Ctrl+C"

# Aguardar interrupção
trap "echo '🛑 Parando serviços...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF

chmod +x run.sh

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "📋 Para executar o projeto:"
echo "   cd ~/mamografia-ia-analysis"
echo "   ./run.sh"
echo ""
echo "⚠️  IMPORTANTE: Configure suas chaves de API em:"
echo "   ~/mamografia-ia-analysis/Backend/.env"
echo ""
echo "🔑 Chaves necessárias:"
echo "   GEMINI_API_KEY=your_gemini_api_key_here"
echo "   HUGGINGFACE_API_KEY=your_huggingface_api_key_here"
echo ""
echo "🎉 Pronto para usar!"

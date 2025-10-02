#!/bin/bash

# =============================================================================
# Script de Instalação - Projeto Mamografia IA Analysis
# Rocky Linux / RHEL / CentOS / AlmaLinux
# =============================================================================

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Função para verificar se o comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para instalar Node.js
install_nodejs() {
    print_status "Instalando Node.js 20.x..."
    
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_status "Node.js já instalado: $NODE_VERSION"
        return
    fi
    
    # Instalar Node.js 20.x via NodeSource
    curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
    sudo dnf install -y nodejs
    
    print_success "Node.js instalado com sucesso"
}

# Função para instalar Python 3.11+
install_python() {
    print_status "Instalando Python 3.11+..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version)
        print_status "Python já instalado: $PYTHON_VERSION"
    else
        sudo dnf install -y python3 python3-pip python3-devel
    fi
    
    # Instalar pip se não existir
    if ! command_exists pip3; then
        sudo dnf install -y python3-pip
    fi
    
    print_success "Python instalado com sucesso"
}

# Função para instalar dependências do sistema
install_system_dependencies() {
    print_status "Instalando dependências do sistema..."
    
    # Atualizar sistema
    sudo dnf update -y
    
    # Instalar dependências essenciais
    sudo dnf groupinstall -y "Development Tools"
    sudo dnf install -y \
        git \
        curl \
        wget \
        unzip \
        gcc \
        gcc-c++ \
        make \
        openssl-devel \
        libffi-devel \
        zlib-devel \
        bzip2-devel \
        readline-devel \
        sqlite-devel \
        tk-devel \
        gdbm-devel \
        db4-devel \
        libpcap-devel \
        xz-devel \
        expat-devel \
        libuuid-devel \
        libffi-devel \
        libssl-devel \
        python3-tkinter \
        python3-pillow \
        python3-devel
    
    print_success "Dependências do sistema instaladas"
}

# Função para configurar firewall
configure_firewall() {
    print_status "Configurando firewall..."
    
    if command_exists firewall-cmd; then
        sudo firewall-cmd --permanent --add-port=8000/tcp
        sudo firewall-cmd --permanent --add-port=5173/tcp
        sudo firewall-cmd --reload
        print_success "Firewall configurado"
    else
        print_warning "Firewall não encontrado, configurando manualmente"
    fi
}

# Função para criar usuário para o projeto
create_project_user() {
    print_status "Criando usuário do projeto..."
    
    if ! id "mamografia" &>/dev/null; then
        sudo useradd -m -s /bin/bash mamografia
        sudo usermod -aG wheel mamografia
        print_success "Usuário 'mamografia' criado"
    else
        print_status "Usuário 'mamografia' já existe"
    fi
}

# Função para clonar o repositório
clone_repository() {
    print_status "Clonando repositório do projeto..."
    
    if [ -d "/home/mamografia/mamografia-ia-analysis" ]; then
        print_status "Repositório já existe, atualizando..."
        cd /home/mamografia/mamografia-ia-analysis
        sudo -u mamografia git pull
    else
        cd /home/mamografia
        sudo -u mamografia git clone https://github.com/Felipensct/mamografia-ia-analysis.git
        cd mamografia-ia-analysis
    fi
    
    print_success "Repositório clonado/atualizado"
}

# Função para instalar dependências do backend
install_backend_dependencies() {
    print_status "Instalando dependências do backend..."
    
    cd /home/mamografia/mamografia-ia-analysis/Backend
    
    # Criar ambiente virtual
    sudo -u mamografia python3 -m venv venv
    sudo -u mamografia ./venv/bin/pip install --upgrade pip
    
    # Instalar dependências
    sudo -u mamografia ./venv/bin/pip install -r requirements.txt
    
    print_success "Dependências do backend instaladas"
}

# Função para instalar dependências do frontend
install_frontend_dependencies() {
    print_status "Instalando dependências do frontend..."
    
    cd /home/mamografia/mamografia-ia-analysis/frontend
    
    # Instalar dependências
    sudo -u mamografia npm install
    
    print_success "Dependências do frontend instaladas"
}

# Função para configurar arquivo .env
configure_env() {
    print_status "Configurando arquivo .env..."
    
    cd /home/mamografia/mamografia-ia-analysis/Backend
    
    if [ ! -f ".env" ]; then
        sudo -u mamografia cp env.example .env
        print_warning "Arquivo .env criado. Configure suas chaves de API:"
        print_warning "  - GEMINI_API_KEY"
        print_warning "  - HUGGINGFACE_API_KEY"
        print_warning "Edite: /home/mamografia/mamografia-ia-analysis/Backend/.env"
    else
        print_status "Arquivo .env já existe"
    fi
}

# Função para criar diretórios necessários
create_directories() {
    print_status "Criando diretórios necessários..."
    
    cd /home/mamografia/mamografia-ia-analysis/Backend
    
    sudo -u mamografia mkdir -p uploads results
    sudo chown -R mamografia:mamografia uploads results
    
    print_success "Diretórios criados"
}

# Função para criar serviços systemd
create_systemd_services() {
    print_status "Criando serviços systemd..."
    
    # Serviço do Backend
    sudo tee /etc/systemd/system/mamografia-backend.service > /dev/null <<EOF
[Unit]
Description=Mamografia IA Analysis Backend
After=network.target

[Service]
Type=simple
User=mamografia
WorkingDirectory=/home/mamografia/mamografia-ia-analysis/Backend
Environment=PATH=/home/mamografia/mamografia-ia-analysis/Backend/venv/bin
ExecStart=/home/mamografia/mamografia-ia-analysis/Backend/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Serviço do Frontend
    sudo tee /etc/systemd/system/mamografia-frontend.service > /dev/null <<EOF
[Unit]
Description=Mamografia IA Analysis Frontend
After=network.target

[Service]
Type=simple
User=mamografia
WorkingDirectory=/home/mamografia/mamografia-ia-analysis/frontend
ExecStart=/usr/bin/npm run dev
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Recarregar systemd
    sudo systemctl daemon-reload
    
    print_success "Serviços systemd criados"
}

# Função para criar script de gerenciamento
create_management_script() {
    print_status "Criando script de gerenciamento..."
    
    sudo tee /usr/local/bin/mamografia <<EOF
#!/bin/bash

# Script de gerenciamento do projeto Mamografia IA Analysis

case "\$1" in
    start)
        echo "Iniciando serviços..."
        sudo systemctl start mamografia-backend
        sudo systemctl start mamografia-frontend
        echo "Serviços iniciados!"
        echo "Backend: http://localhost:8000"
        echo "Frontend: http://localhost:5173"
        ;;
    stop)
        echo "Parando serviços..."
        sudo systemctl stop mamografia-backend
        sudo systemctl stop mamografia-frontend
        echo "Serviços parados!"
        ;;
    restart)
        echo "Reiniciando serviços..."
        sudo systemctl restart mamografia-backend
        sudo systemctl restart mamografia-frontend
        echo "Serviços reiniciados!"
        ;;
    status)
        echo "Status dos serviços:"
        sudo systemctl status mamografia-backend --no-pager
        echo ""
        sudo systemctl status mamografia-frontend --no-pager
        ;;
    logs)
        echo "Logs do backend:"
        sudo journalctl -u mamografia-backend -f
        ;;
    logs-frontend)
        echo "Logs do frontend:"
        sudo journalctl -u mamografia-frontend -f
        ;;
    update)
        echo "Atualizando projeto..."
        cd /home/mamografia/mamografia-ia-analysis
        sudo -u mamografia git pull
        echo "Projeto atualizado!"
        ;;
    install)
        echo "Reinstalando dependências..."
        cd /home/mamografia/mamografia-ia-analysis/Backend
        sudo -u mamografia ./venv/bin/pip install -r requirements.txt
        cd /home/mamografia/mamografia-ia-analysis/frontend
        sudo -u mamografia npm install
        echo "Dependências reinstaladas!"
        ;;
    *)
        echo "Uso: mamografia {start|stop|restart|status|logs|logs-frontend|update|install}"
        echo ""
        echo "Comandos disponíveis:"
        echo "  start          - Iniciar todos os serviços"
        echo "  stop           - Parar todos os serviços"
        echo "  restart        - Reiniciar todos os serviços"
        echo "  status         - Ver status dos serviços"
        echo "  logs           - Ver logs do backend"
        echo "  logs-frontend  - Ver logs do frontend"
        echo "  update         - Atualizar código do projeto"
        echo "  install        - Reinstalar dependências"
        ;;
esac
EOF

    sudo chmod +x /usr/local/bin/mamografia
    
    print_success "Script de gerenciamento criado: /usr/local/bin/mamografia"
}

# Função para criar script de build de produção
create_build_script() {
    print_status "Criando script de build de produção..."
    
    sudo tee /usr/local/bin/mamografia-build <<EOF
#!/bin/bash

# Script para build de produção do frontend

echo "Construindo frontend para produção..."

cd /home/mamografia/mamografia-ia-analysis/frontend

# Instalar dependências
sudo -u mamografia npm install

# Build de produção
sudo -u mamografia npm run build

echo "Build concluído! Arquivos em: /home/mamografia/mamografia-ia-analysis/frontend/dist"
echo "Para servir os arquivos estáticos, use um servidor web como nginx."
EOF

    sudo chmod +x /usr/local/bin/mamografia-build
    
    print_success "Script de build criado: /usr/local/bin/mamografia-build"
}

# Função para configurar nginx (opcional)
configure_nginx() {
    print_status "Configurando nginx (opcional)..."
    
    if command_exists nginx; then
        print_status "Nginx já instalado"
    else
        sudo dnf install -y nginx
    fi
    
    # Configuração do nginx
    sudo tee /etc/nginx/conf.d/mamografia.conf > /dev/null <<EOF
server {
    listen 80;
    server_name localhost;
    
    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Uploads
    location /uploads/ {
        proxy_pass http://localhost:8000/uploads/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # Testar configuração
    sudo nginx -t
    
    if [ $? -eq 0 ]; then
        sudo systemctl enable nginx
        sudo systemctl start nginx
        print_success "Nginx configurado e iniciado"
    else
        print_error "Erro na configuração do nginx"
    fi
}

# Função para criar backup automático
create_backup_script() {
    print_status "Criando script de backup..."
    
    sudo tee /usr/local/bin/mamografia-backup <<EOF
#!/bin/bash

# Script de backup do projeto

BACKUP_DIR="/home/mamografia/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="mamografia_backup_\$DATE.tar.gz"

echo "Criando backup do projeto..."

# Criar diretório de backup
sudo -u mamografia mkdir -p \$BACKUP_DIR

# Fazer backup
cd /home/mamografia
sudo -u mamografia tar -czf \$BACKUP_DIR/\$BACKUP_FILE mamografia-ia-analysis/

echo "Backup criado: \$BACKUP_DIR/\$BACKUP_FILE"

# Manter apenas os últimos 7 backups
sudo -u mamografia find \$BACKUP_DIR -name "mamografia_backup_*.tar.gz" -mtime +7 -delete

echo "Backup concluído!"
EOF

    sudo chmod +x /usr/local/bin/mamografia-backup
    
    # Adicionar ao crontab
    (sudo -u mamografia crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/mamografia-backup") | sudo -u mamografia crontab -
    
    print_success "Script de backup criado e agendado"
}

# Função principal
main() {
    echo "============================================================================="
    echo "🚀 Instalação do Projeto Mamografia IA Analysis - Rocky Linux"
    echo "============================================================================="
    echo ""
    
    # Verificar se é root
    if [ "$EUID" -eq 0 ]; then
        print_error "Não execute este script como root. Execute como usuário normal."
        exit 1
    fi
    
    # Verificar se tem sudo
    if ! sudo -n true 2>/dev/null; then
        print_error "Este script precisa de privilégios sudo. Configure sudo primeiro."
        exit 1
    fi
    
    print_status "Iniciando instalação..."
    
    # Instalar dependências do sistema
    install_system_dependencies
    
    # Instalar Python
    install_python
    
    # Instalar Node.js
    install_nodejs
    
    # Configurar firewall
    configure_firewall
    
    # Criar usuário do projeto
    create_project_user
    
    # Clonar repositório
    clone_repository
    
    # Instalar dependências do backend
    install_backend_dependencies
    
    # Instalar dependências do frontend
    install_frontend_dependencies
    
    # Configurar .env
    configure_env
    
    # Criar diretórios
    create_directories
    
    # Criar serviços systemd
    create_systemd_services
    
    # Criar script de gerenciamento
    create_management_script
    
    # Criar script de build
    create_build_script
    
    # Criar script de backup
    create_backup_script
    
    # Perguntar sobre nginx
    echo ""
    read -p "Deseja configurar nginx para proxy reverso? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        configure_nginx
    fi
    
    echo ""
    echo "============================================================================="
    print_success "Instalação concluída com sucesso!"
    echo "============================================================================="
    echo ""
    echo "📋 Próximos passos:"
    echo ""
    echo "1. Configure suas chaves de API:"
    echo "   sudo nano /home/mamografia/mamografia-ia-analysis/Backend/.env"
    echo ""
    echo "2. Inicie os serviços:"
    echo "   mamografia start"
    echo ""
    echo "3. Verifique o status:"
    echo "   mamografia status"
    echo ""
    echo "4. Acesse a aplicação:"
    echo "   Frontend: http://localhost:5173"
    echo "   Backend:  http://localhost:8000"
    echo "   Docs:     http://localhost:8000/docs"
    echo ""
    echo "📚 Comandos úteis:"
    echo "   mamografia start     - Iniciar serviços"
    echo "   mamografia stop      - Parar serviços"
    echo "   mamografia restart   - Reiniciar serviços"
    echo "   mamografia status    - Ver status"
    echo "   mamografia logs      - Ver logs do backend"
    echo "   mamografia update    - Atualizar projeto"
    echo "   mamografia-backup    - Fazer backup"
    echo "   mamografia-build     - Build de produção"
    echo ""
    echo "🔧 Configuração do .env:"
    echo "   GEMINI_API_KEY=your_gemini_api_key_here"
    echo "   HUGGINGFACE_API_KEY=your_huggingface_api_key_here"
    echo ""
    print_success "Instalação finalizada!"
}

# Executar função principal
main "$@"

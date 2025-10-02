# 🏥 Plataforma de Análise de Mamografias com IA

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.4+-4FC08D.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Sistema completo para análise inteligente de imagens de mamografia utilizando múltiplas APIs de IA**

[🚀 Instalação](#-instalação) • [🔧 Configuração](#-configuração) • [🎯 Funcionalidades](#-funcionalidades) • [📖 Documentação](#-documentação)

</div>

---

## 📋 Sobre o Projeto

Plataforma web completa que permite analisar imagens de mamografia utilizando **Inteligência Artificial**. O sistema integra múltiplas APIs de IA (Google Gemini e Hugging Face) para fornecer análises técnicas detalhadas e comparativas.

### 🎯 Objetivos
- **Análise Inteligente**: Processamento de imagens de mamografia com IA
- **Comparação de Modelos**: Múltiplas APIs para análise comparativa
- **Interface Intuitiva**: Frontend moderno e responsivo
- **Armazenamento Seguro**: Banco de dados para histórico de análises

### 👥 Equipe
- **Felipe Nascimento da Silva** - Desenvolvimento Full-Stack
- **Enzo Carvalho Mattiotti dos Reis** - Desenvolvimento Backend
- **João Pedro Carvalho** - Desenvolvimento Frontend

---

## 🚀 Instalação

### **Opção 1: Instalação Automática (Recomendado)**

```bash
# Baixar e executar script de instalação
curl -O https://raw.githubusercontent.com/Felipensct/mamografia-ia-analysis/main/install_rocky_linux.sh
chmod +x install_rocky_linux.sh
./install_rocky_linux.sh

# Configurar chaves de API
sudo nano /home/mamografia/mamografia-ia-analysis/Backend/.env

# Iniciar serviços
mamografia start
```

### **Opção 2: Instalação Manual**

```bash
# 1. Clonar repositório
git clone https://github.com/Felipensct/mamografia-ia-analysis.git
cd mamografia-ia-analysis

# 2. Backend
cd Backend
pip3 install -r requirements.txt
cp env.example .env
# Editar .env com suas chaves de API
python3 app.py

# 3. Frontend (novo terminal)
cd frontend
npm install
npm run dev
```

### **Opção 3: Docker**

```bash
# Clonar e configurar
git clone https://github.com/Felipensct/mamografia-ia-analysis.git
cd mamografia-ia-analysis
cp env.example .env
# Editar .env com suas chaves

# Executar com Docker
docker-compose up -d
```

---

## 🔧 Configuração

### **Chaves de API Necessárias**

1. **Google Gemini**: https://makersuite.google.com/app/apikey
2. **Hugging Face**: https://huggingface.co/settings/tokens

### **Arquivo .env**

```env
# Chaves de API (OBRIGATÓRIO)
GEMINI_API_KEY=your_gemini_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Configurações do Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Configurações do Frontend
VITE_API_URL=http://localhost:8000
```

---

## 🎯 Funcionalidades

### ✅ **Backend (FastAPI)**
- **Upload de Imagens**: Validação e processamento de imagens de mamografia
- **Integração IA**: Google Gemini + Hugging Face com fallback automático
- **Banco de Dados**: SQLite com SQLAlchemy ORM
- **API REST**: Endpoints documentados com Swagger UI
- **Processamento**: Otimização de imagens (resolução, contraste, brilho)

### ✅ **Frontend (Vue.js)**
- **Interface Moderna**: Design responsivo e intuitivo
- **Upload Drag & Drop**: Interface amigável para envio de imagens
- **Dashboard Interativo**: Estatísticas e visualizações em tempo real
- **Lista de Análises**: Histórico completo com filtros e busca
- **Visualização de Resultados**: Exibição detalhada das análises de IA

### ✅ **Integração IA**
- **Google Gemini**: Análise técnica detalhada com prompt otimizado
- **Hugging Face**: Fallback automático para modelos alternativos
- **Processamento Inteligente**: Otimização de imagens para melhor análise
- **Status Tracking**: Acompanhamento em tempo real do processamento

---

## 🔌 API Endpoints

### **Upload e Gerenciamento**
- `POST /api/v1/upload` - Upload de imagem de mamografia
- `GET /api/v1/analyses` - Listar todas as análises
- `GET /api/v1/analysis/{id}` - Detalhes de uma análise específica

### **Análise com IA**
- `POST /api/v1/analyze/{id}` - Análise com Gemini (fallback Hugging Face)
- `POST /api/v1/analyze-huggingface/{id}` - Análise direta com Hugging Face

### **Utilitários**
- `GET /health` - Status da API
- `GET /uploads/{filename}` - Servir imagens enviadas
- `GET /docs` - Swagger UI interativo

---

## 🚀 Deploy e Produção

### **Comandos de Gerenciamento**

```bash
# Systemd (após instalação completa)
mamografia start      # Iniciar serviços
mamografia stop       # Parar serviços
mamografia restart    # Reiniciar serviços
mamografia status     # Ver status
mamografia logs       # Ver logs

# Docker
docker-compose up -d        # Iniciar
docker-compose down         # Parar
docker-compose logs         # Ver logs
```

---

## 🧪 Testes

### **Teste Manual**
1. Acesse http://localhost:5173
2. Faça upload de uma imagem de mamografia
3. Execute a análise
4. Visualize os resultados

### **Teste da API**
```bash
# Backend
cd Backend && python3 test_api.py

# Frontend
cd frontend && npm run test
```

---

## 🐛 Solução de Problemas

### **Erro: "Address already in use"**
```bash
sudo lsof -ti:8000 | xargs sudo kill -9
sudo lsof -ti:5173 | xargs sudo kill -9
```

### **Erro: "API Key not found"**
```bash
# Verificar arquivo .env
ls -la Backend/.env
cat Backend/.env
```

### **Erro: "Module not found"**
```bash
# Backend
cd Backend && pip3 install -r requirements.txt

# Frontend
cd frontend && npm install
```

---

## 📊 Métricas do Projeto

| Componente | Linhas de Código | Arquivos | Funcionalidades |
|------------|------------------|----------|-----------------|
| **Backend** | ~500 | 8 | 7 endpoints |
| **Frontend** | ~800 | 15 | 4 componentes |
| **Total** | ~1300 | 23+ | 20+ funcionalidades |

---

## 📖 Documentação

- **Backend API Docs**: http://localhost:8000/docs
- **Frontend Components**: [./frontend/README.md](./frontend/README.md)
- **Backend Details**: [./Backend/README.md](./Backend/README.md)

---

## 📞 Suporte

- **Email**: felipe.nascimento@univap.br
- **GitHub**: [@Felipensct](https://github.com/Felipensct)
- **Issues**: [GitHub Issues](https://github.com/Felipensct/mamografia-ia-analysis/issues)

---

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

---

<div align="center">

**🏆 Projeto desenvolvido para a matéria Projetos IV de Engenharia da Computação**

**Universidade do Vale do Paraíba - 2025**

[⬆ Voltar ao topo](#-plataforma-de-análise-de-mamografias-com-ia)

</div>
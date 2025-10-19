# Plataforma de Análise de Mamografias com IA

Sistema completo para análise inteligente de imagens de mamografia utilizando múltiplas APIs de IA com arquitetura híbrida robusta.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4+-4FC08D.svg)](https://vuejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Produção-success.svg)](https://github.com/Felipensct/mamografia-ia-analysis)

## Visão Geral

A plataforma implementa um sistema híbrido de análise de mamografias com três camadas de Inteligência Artificial:

1. **Google Gemini 2.0 Flash** - Análise médica especializada com classificação BI-RADS
2. **Hugging Face Transformers** - Complemento técnico computacional
3. **Análise Local OpenCV** - Fallback robusto sempre disponível

### Características Principais

- ✅ **Sistema híbrido robusto** que nunca falha
- ✅ **Classificação BI-RADS** integrada
- ✅ **Interface moderna** com design system médico
- ✅ **Análise estruturada** em Markdown com priorização visual
- ✅ **Clean Architecture** no backend
- ✅ **TypeScript** no frontend
- ✅ **Docker** para containerização
- ✅ **Documentação completa** seguindo padrões da indústria

## Início Rápido

### Instalação Automática (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/Felipensct/mamografia-ia-analysis.git
cd mamografia-ia-analysis

# 2. Configure suas chaves de API
cp Backend/env.example Backend/.env
nano Backend/.env  # Adicione suas chaves

# 3. Execute o script de inicialização
./start.sh
```

### Acesso à Aplicação

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Documentação

### 📚 Documentação

- **[Arquitetura do Sistema](docs/ARCHITECTURE.md)** - Decisões técnicas e estrutura
- **[Changelog](docs/CHANGELOG.md)** - Histórico de mudanças e melhorias

## Arquitetura

### Sistema Híbrido de IA

```
┌─────────────────────────────────────────┐
│          FRONTEND (Vue.js 3)            │
│  - Upload de imagens                    │
│  - Visualização de análises             │
│  - Renderização Markdown                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         BACKEND (FastAPI)               │
│  - API REST                             │
│  - Processamento de imagens             │
│  - Banco de dados SQLite                │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌─────────┐         ┌──────────────┐
│ Gemini  │         │  Hugging Face│
│  2.0    │         │  + Local     │
│ Flash   │         │  OpenCV      │
└─────────┘         └──────────────┘
   (Principal)        (Complemento)
```

### Stack Tecnológico

**Backend**
- FastAPI (Python 3.11+)
- SQLAlchemy ORM
- OpenCV para processamento de imagem
- Google Gemini 2.0 Flash
- Hugging Face Transformers

**Frontend**
- Vue.js 3 com TypeScript
- Tailwind CSS
- Pinia para estado
- Marked.js para renderização

## Funcionalidades

### Análise de Imagens
- Upload de imagens de mamografia
- Processamento automático (redimensionamento, contraste)
- Análise híbrida com múltiplas IAs
- Classificação BI-RADS integrada
- Priorização visual de achados

### Interface do Usuário
- Dashboard moderno com estatísticas
- Image viewer com controles de zoom
- Tabs organizadas por tipo de análise
- Renderização Markdown estruturada
- Sistema de notificações Toast

### Sistema Robusto
- Fallback inteligente entre IAs
- Análise local sempre disponível
- Validação rigorosa de arquivos
- Logs estruturados
- Health checks

## Configuração

### Variáveis de Ambiente

**Backend (.env)**
```env
GEMINI_API_KEY=your_gemini_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

**Frontend (.env.local)**
```env
VITE_API_URL=http://localhost:8000
```

### Chaves de API Necessárias

1. **Google Gemini**: [Obter chave](https://makersuite.google.com/app/apikey)
2. **Hugging Face**: [Obter token](https://huggingface.co/settings/tokens)

## Execução

### Desenvolvimento
```bash
# Backend
cd Backend
source venv/bin/activate
python app.py

# Frontend (novo terminal)
cd frontend
npm run dev
```

### Produção
```bash
# Docker Compose
docker-compose up -d

# Ou com systemd (após instalação completa)
mamografia start
```

## API Endpoints

### Upload e Gerenciamento
- `POST /api/v1/upload` - Upload de imagem
- `GET /api/v1/analyses` - Listar análises
- `GET /api/v1/analysis/{id}` - Detalhes da análise
- `DELETE /api/v1/analysis/{id}` - Excluir análise

### Análise com IA
- `POST /api/v1/analyze/{id}` - Análise com Gemini
- `POST /api/v1/analyze-huggingface/{id}` - Análise com Hugging Face

### Utilitários
- `GET /health` - Status da API
- `GET /uploads/{filename}` - Servir imagens
- `GET /docs` - Swagger UI

## Testes

### Backend
```bash
cd Backend
python test_api.py
python test_huggingface_analysis.py
```

### Frontend
```bash
cd frontend
npm run test
```

## Troubleshooting

### Problemas Comuns

**Erro: "Address already in use"**
```bash
sudo lsof -ti:8000 | xargs sudo kill -9
sudo lsof -ti:5173 | xargs sudo kill -9
```

**Erro: "API Key not found"**
```bash
cat Backend/.env | grep API_KEY
```

**Erro: "table analyses has no column named info"**
```bash
cd Backend
python migrate_database.py
```

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Equipe

- **Felipe Nascimento da Silva** - Desenvolvimento Full-Stack
- **Enzo Carvalho Mattiotti dos Reis** - Desenvolvimento Backend
- **João Pedro Carvalho** - Desenvolvimento Frontend

**Universidade do Vale do Paraíba - Projetos IV - 2025**

## Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

## Suporte

- **Email**: felipe.nascimento@univap.br
- **GitHub**: [@Felipensct](https://github.com/Felipensct)
- **Issues**: [GitHub Issues](https://github.com/Felipensct/mamografia-ia-analysis/issues)

---

**Desenvolvido para fins acadêmicos - UNIVAP 2025**
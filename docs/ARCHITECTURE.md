# Arquitetura do Sistema - Plataforma de Análise de Mamografias com IA

## Visão Geral

A plataforma implementa uma arquitetura híbrida para análise de imagens de mamografia utilizando múltiplas abordagens de Inteligência Artificial, seguindo princípios de Clean Architecture e boas práticas de engenharia de software.

## Stack Tecnológico

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Banco de Dados**: SQLite com SQLAlchemy ORM
- **Processamento de Imagem**: OpenCV, PIL (Pillow)
- **IA**: Google Gemini 2.0 Flash, Hugging Face Transformers
- **Validação**: Pydantic models

### Frontend
- **Framework**: Vue.js 3 com TypeScript
- **Build Tool**: Vite
- **UI Library**: Tailwind CSS
- **Estado**: Pinia
- **Roteamento**: Vue Router

### Infraestrutura
- **Containerização**: Docker + Docker Compose
- **Proxy Reverso**: Nginx
- **Deploy**: Scripts automatizados para Rocky Linux

## Decisões de Design

### 1. Sistema Híbrido de IA

A arquitetura implementa um sistema híbrido de análise com três camadas:

```
┌─────────────────────────────────────────┐
│          FRONTEND (Vue.js 3)            │
│  - Upload de imagens                    │
│  - Visualização de análises             │
│  - Renderização Markdown                │
│  - Gestão de estado (Pinia)             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         BACKEND (FastAPI)               │
│  - API REST                             │
│  - Processamento de imagens             │
│  - Banco de dados SQLite                │
│  - Sistema de IA híbrido                │
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

#### Camada 1: Google Gemini (Principal)
- **Propósito**: Análise médica especializada
- **Características**: 
  - Prompt otimizado para mamografias
  - Classificação BI-RADS integrada
  - Estrutura Markdown estruturada
  - Priorização de achados (crítico/importante/observação)

#### Camada 2: Hugging Face (Complemento)
- **Propósito**: Análise computacional complementar
- **Características**:
  - Modelos de visão computacional
  - Interpretação contextual para mamografia
  - Limitações claramente documentadas
  - Fallback para análise local

#### Camada 3: Análise Local OpenCV (Fallback)
- **Propósito**: Análise técnica robusta sempre disponível
- **Características**:
  - Análise estatística de densidade
  - Detecção de bordas (Canny)
  - Medição de nitidez (Laplacian)
  - Score de qualidade (0-100)

### 2. Clean Architecture no Backend

```
Backend/
├── app.py                 # Camada de apresentação (FastAPI)
├── services/              # Camada de aplicação
│   ├── ai_service.py      # Serviços de IA
│   └── multi_ai_service.py # Serviços multi-IA
├── models/                # Camada de domínio (SQLAlchemy)
└── database/              # Camada de infraestrutura
```

#### Princípios Aplicados:
- **Separação de responsabilidades**: Cada camada tem responsabilidade específica
- **Inversão de dependência**: Camadas superiores não dependem de implementações específicas
- **Testabilidade**: Estrutura facilita testes unitários e de integração

### 3. Design System do Frontend

#### CSS Variables e Design System
```css
:root {
  /* Paleta de Cores Médicas */
  --color-primary-600: #0284c7;  /* Azul médico profissional */
  --color-success-600: #16a34a;   /* Verde para sucesso */
  --color-warning-600: #d97706;   /* Amarelo para atenção */
  --color-danger-600: #dc2626;    /* Vermelho para erros */
  
  /* Gradientes Médicos */
  --gradient-primary: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
  --gradient-success: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
  
  /* Sombras Profissionais */
  --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  
  /* Transições Suaves */
  --transition-fast: 0.15s ease-in-out;
  --transition-base: 0.2s ease-in-out;
  --transition-slow: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

#### Componentes Principais:
- **Stat Cards**: Cards de estatísticas com hover effects
- **Analysis Cards**: Cards de análise com status bar colorida
- **Image Viewer**: Visualizador com controles de zoom
- **Method Selector**: Seleção de método de IA
- **Empty States**: Estados vazios com CTAs

## Estrutura de Diretórios

```
mamografia-ia-analysis/
├── Backend/                    # API FastAPI
│   ├── app.py                  # Aplicação principal
│   ├── services/               # Serviços de negócio
│   │   ├── ai_service.py       # Serviço de IA híbrido
│   │   └── multi_ai_service.py # Serviço multi-IA
│   ├── requirements.txt        # Dependências Python
│   ├── migrate_database.py     # Migração de banco
│   └── rebuild_venv.sh         # Script de reconstrução
├── frontend/                   # Aplicação Vue.js
│   ├── src/
│   │   ├── components/         # Componentes Vue
│   │   │   ├── AnalysisDetail.vue
│   │   │   ├── AnalysisList.vue
│   │   │   ├── ImageUpload.vue
│   │   │   └── Toast.vue
│   │   ├── views/              # Páginas
│   │   │   ├── HomeView.vue
│   │   │   ├── AnalysesView.vue
│   │   │   └── AnalysisDetailView.vue
│   │   ├── services/           # Serviços de API
│   │   ├── stores/             # Gerenciamento de estado
│   │   └── composables/        # Composables Vue
│   ├── package.json
│   └── vite.config.ts
├── docs/                       # Documentação
│   ├── ARCHITECTURE.md         # Este arquivo
│   ├── DEVELOPMENT.md          # Guia de desenvolvimento
│   ├── DEPLOYMENT.md           # Guia de deploy
│   └── CHANGELOG.md            # Histórico de mudanças
├── docker-compose.yml          # Orquestração de containers
├── nginx.conf                  # Configuração do proxy
└── README.md                   # Documentação principal
```

## Fluxo de Dados

### 1. Upload e Processamento
```
1. Usuário faz upload → Frontend (Vue.js)
2. Validação de formato → Backend (FastAPI)
3. Processamento de imagem → OpenCV/PIL
4. Armazenamento → SQLite
5. Resposta → Frontend
```

### 2. Análise com IA
```
1. Usuário solicita análise → Frontend
2. Seleção de método → Backend
3. Tentativa Gemini → Google API
4. Se falhar → Hugging Face API
5. Se falhar → Análise local OpenCV
6. Formatação resultado → Markdown
7. Armazenamento → SQLite
8. Renderização → Frontend
```

### 3. Visualização
```
1. Carregamento análise → Frontend
2. Parse Markdown → marked.js
3. Aplicação estilos → CSS customizado
4. Renderização → DOM
```

## Integrações com APIs Externas

### Google Gemini 2.0 Flash
- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent`
- **Autenticação**: API Key
- **Formato**: JSON com prompt estruturado
- **Rate Limiting**: Implementado com retry logic

### Hugging Face Transformers
- **Endpoint**: `https://api-inference.huggingface.co/models/{model_name}`
- **Autenticação**: API Token
- **Modelos**: ConvNeXt, Swin Transformer, ResNet-50, Vision Transformer
- **Fallback**: Análise local OpenCV

## Padrões de Código

### Backend (Python)
- **Type Hints**: Uso obrigatório de type hints
- **Docstrings**: Documentação de funções e classes
- **Error Handling**: Tratamento robusto de exceções
- **Logging**: Logs estruturados para debugging

### Frontend (TypeScript/Vue)
- **Composition API**: Uso preferencial do Composition API
- **TypeScript**: Tipagem forte em todos os componentes
- **Reactive**: Uso adequado de ref() e computed()
- **Props Validation**: Validação de props com TypeScript

## Decisões Técnicas Importantes

### 1. Sistema de Fallback Inteligente
**Decisão**: Implementar sistema híbrido com múltiplas camadas de análise
**Justificativa**: Garantir robustez e sempre retornar análise útil, mesmo com falhas de API

### 2. Classificação BI-RADS Integrada
**Decisão**: Integrar classificação BI-RADS no prompt do Gemini
**Justificativa**: Padrão médico reconhecido internacionalmente para mamografias

### 3. Renderização Markdown
**Decisão**: Usar Markdown para formatação de análises
**Justificativa**: Flexibilidade de formatação e facilidade de manutenção

### 4. Design System com CSS Variables
**Decisão**: Implementar design system baseado em CSS variables
**Justificativa**: Consistência visual e facilidade de manutenção

### 5. Clean Architecture
**Decisão**: Seguir princípios de Clean Architecture
**Justificativa**: Manutenibilidade, testabilidade e separação de responsabilidades

## Considerações de Performance

### Backend
- **Processamento de Imagem**: Otimização automática (redimensionamento, contraste)
- **Cache**: Implementação de cache para análises frequentes
- **Async/Await**: Uso de operações assíncronas para APIs externas

### Frontend
- **Lazy Loading**: Carregamento sob demanda de componentes
- **Virtual Scrolling**: Para listas grandes de análises
- **Image Optimization**: Compressão e otimização de imagens

## Segurança

### API Security
- **CORS**: Configuração adequada de CORS
- **Input Validation**: Validação rigorosa de inputs
- **File Upload**: Validação de tipos e tamanhos de arquivo

### Data Protection
- **Local Storage**: Dados sensíveis não armazenados localmente
- **API Keys**: Gerenciamento seguro de chaves de API
- **HTTPS**: Uso obrigatório em produção

## Monitoramento e Logs

### Logging Strategy
- **Structured Logging**: Logs em formato JSON
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Context**: Inclusão de contexto relevante nos logs

### Health Checks
- **API Health**: Endpoint `/health` para monitoramento
- **Database Health**: Verificação de conectividade
- **External APIs**: Monitoramento de disponibilidade

## Escalabilidade

### Horizontal Scaling
- **Stateless Backend**: Backend sem estado para escalabilidade horizontal
- **Database**: SQLite pode ser migrado para PostgreSQL/MySQL
- **Load Balancing**: Nginx configurado para load balancing

### Vertical Scaling
- **Resource Optimization**: Otimização de uso de CPU e memória
- **Caching**: Implementação de cache em múltiplas camadas
- **Database Optimization**: Índices e queries otimizadas

Esta arquitetura garante robustez, manutenibilidade e escalabilidade, seguindo as melhores práticas de engenharia de software e adequando-se às necessidades específicas de análise médica de imagens.

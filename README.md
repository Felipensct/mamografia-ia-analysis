# Mamografia IA

Plataforma de análise automatizada de mamografias utilizando inteligência artificial para classificação BI-RADS e detecção de anomalias.

## Visão Geral

Sistema web desenvolvido para auxiliar profissionais de saúde na análise de imagens mamográficas através de algoritmos de IA avançados. A plataforma oferece análise técnica detalhada seguindo padrões MIAS (Mammographic Image Analysis Society) e classificação BI-RADS.

### Funcionalidades Principais

- **Upload de Imagens**: Suporte para formatos DICOM (.dcm), JPEG, PNG e outros formatos médicos
- **Análise com IA**: Processamento utilizando Google Gemini AI para classificação precisa
- **Classificação BI-RADS**: Categorização automática de achados mamográficos
- **Interface Responsiva**: Dashboard moderno e intuitivo para visualização de resultados
- **Gestão de Análises**: Histórico completo com controle de status e exclusão em lote

### Tecnologias Utilizadas

**Backend**
- Python 3.12+ com FastAPI
- SQLAlchemy para persistência de dados
- Google Generative AI (Gemini)
- OpenCV para processamento de imagens
- PyDICOM para manipulação de arquivos médicos

**Frontend**
- Vue.js 3 com Composition API
- TypeScript para tipagem estática
- Tailwind CSS para estilização
- Pinia para gerenciamento de estado
- Axios para comunicação HTTP

**Infraestrutura**
- Docker e Docker Compose
- Nginx como proxy reverso
- SQLite para desenvolvimento local

## Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Frontend    │    │     Backend     │    │   AI Services   │
│   (Vue.js 3)    │◄──►│   (FastAPI)     │◄──►│  (Gemini AI)    │
│   Port: 5173    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
                   │
         ┌─────────────────┐
         │     Nginx       │
         │   Port: 80      │
         └─────────────────┘
```

## Instalação e Configuração

### Pré-requisitos

- Docker e Docker Compose
- Node.js 20.19+ ou 22.12+
- Python 3.12+
- Chave de API do Google Gemini

### Configuração Rápida

1. **Clone o repositório**
   ```bash
   git clone <repository-url>
   cd ProjetosIV
   ```

2. **Configure as variáveis de ambiente**
   ```bash
   cp env.example .env
   ```
   
   Edite o arquivo `.env` com suas chaves de API:
   ```env
   GEMINI_API_KEY=sua_chave_gemini_aqui
   HUGGINGFACE_API_KEY=sua_chave_huggingface_aqui
   ```

3. **Execute com Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Acesse a aplicação**
   - Interface web: http://localhost
   - API backend: http://localhost:8000
   - Documentação API: http://localhost:8000/docs

### Instalação Manual

**Backend**
```bash
cd Backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Uso da Aplicação

### Fluxo de Análise

1. **Upload de Imagem**: Faça upload de uma mamografia nos formatos suportados
2. **Processamento**: O sistema converte e processa a imagem automaticamente
3. **Análise com IA**: Clique em "Analisar com Gemini" para iniciar a análise
4. **Visualização**: Revise os resultados técnicos e a explicação simplificada
5. **Gestão**: Gerencie o histórico de análises na dashboard principal

### Formatos Suportados

- **DICOM** (.dcm) - Formato padrão médico
- **JPEG** (.jpg, .jpeg) - Imagens comprimidas
- **PNG** (.png) - Imagens sem compressão
- **TIFF** (.tiff, .tif) - Imagens de alta qualidade
- **BMP** (.bmp) - Bitmap
- **PGM** (.pgm) - Portable Graymap

### Estrutura da Resposta IA

A análise retorna informações estruturadas seguindo padrões MIAS:

- **Tipo de tecido**: Classificação da densidade mamária (F/G/D)
- **Classe de anormalidade**: Tipo de achado (CALC/MASS/ARCH/ASYM)
- **Severidade**: Classificação BI-RADS (B/M/U)
- **Localização**: Coordenadas e raio da anomalia
- **Explicação**: Interpretação em linguagem acessível

## Estrutura do Projeto

```
ProjetosIV/
├── Backend/                 # API FastAPI
│   ├── app.py              # Aplicação principal
│   ├── services/           # Serviços de IA
│   ├── requirements.txt    # Dependências Python
│   └── uploads/           # Armazenamento de imagens
├── frontend/              # Interface Vue.js
│   ├── src/
│   │   ├── components/    # Componentes reutilizáveis
│   │   ├── views/         # Páginas da aplicação
│   │   ├── services/      # Comunicação com API
│   │   └── stores/        # Gerenciamento de estado
│   └── package.json       # Dependências Node.js
├── docs/                  # Documentação técnica
├── docker-compose.yml     # Orquestração de containers
└── nginx.conf            # Configuração do proxy
```

## API Endpoints

### Principais Rotas

- `GET /health` - Status da aplicação
- `POST /api/v1/upload` - Upload de imagens
- `GET /api/v1/analyses` - Listar análises
- `GET /api/v1/analysis/{id}` - Detalhes de análise
- `POST /api/v1/analyze/{id}` - Executar análise IA
- `DELETE /api/v1/analysis/{id}` - Excluir análise

### Documentação Completa

Acesse http://localhost:8000/docs para documentação interativa da API.

## Desenvolvimento

### Scripts Disponíveis

**Frontend**
```bash
npm run dev          # Servidor de desenvolvimento
npm run build        # Build para produção
npm run type-check   # Verificação de tipos
npm run lint         # Linting e formatação
```

**Backend**
```bash
python test_api.py   # Testes da API
python migrate_database.py  # Migração do banco
```

### Padrões de Código

- **Clean Architecture** para organização de código
- **TypeScript** para tipagem estática no frontend
- **Pydantic** para validação de dados no backend
- **ESLint** e **Prettier** para formatação consistente

## Limitações e Considerações

### Técnicas

- Análise limitada a imagens 2D
- Processamento sequencial (não paralelo)
- Armazenamento local (SQLite)
- Dependência de conectividade para APIs externas

### Médicas

- **Ferramenta auxiliar**: Não substitui diagnóstico médico profissional
- **Validação necessária**: Resultados devem ser validados por radiologista
- **Uso educacional**: Adequado para treinamento e segunda opinião

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para detalhes.

## Suporte

Para questões técnicas ou sugestões:

- Abra uma issue no repositório
- Consulte a documentação em `/docs`
- Verifique os logs da aplicação para debugging

---

**Aviso Legal**: Esta aplicação é destinada apenas para fins educacionais e de pesquisa. Não deve ser utilizada como única ferramenta para diagnóstico médico. Sempre consulte um profissional de saúde qualificado para interpretação de resultados médicos.
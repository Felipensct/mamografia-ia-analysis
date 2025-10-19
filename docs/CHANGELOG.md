# Changelog - Plataforma de Análise de Mamografias com IA

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [2.0.0] - 2025-10-09

### Adicionado
- **Sistema híbrido de IA** com três camadas de análise
  - Google Gemini 2.0 Flash como análise principal
  - Hugging Face Transformers como complemento técnico
  - Análise local OpenCV como fallback robusto
- **Classificação BI-RADS integrada** no prompt do Gemini
- **Prompt otimizado** com estrutura Markdown de 9 seções
- **Priorização de achados** com sistema visual (🔴 Crítico, 🟡 Importante, 🟢 Observação)
- **Níveis de confiança** (Alta/Média/Baixa) nas análises
- **Recomendações específicas** com checkboxes
- **Campo `info`** no banco de dados para metadados de processamento
- **Renderização Markdown** no frontend com biblioteca `marked`
- **Design system completo** com 50+ variáveis CSS
- **7 animações profissionais** (fadeIn, medicalPulse, pulseGlow, etc.)
- **Image viewer avançado** com controles de zoom (1x-3x)
- **Tabs de análise** (Gemini, Hugging Face, Metadados, Comparação)
- **Sistema de fallback inteligente** que nunca falha
- **Análise local robusta** com OpenCV para processamento de imagem
- **Scripts de migração** de banco de dados
- **Documentação consolidada** em estrutura padrão da indústria

### Alterado
- **Arquitetura do sistema** para Clean Architecture
- **Interface do usuário** completamente modernizada
- **Sistema de notificações** com Toast component
- **Processamento de imagens** com otimização automática
- **Validação de arquivos** mais rigorosa
- **Estrutura de diretórios** organizada seguindo padrões
- **Sistema de logging** estruturado

### Corrigido
- **Botão de exclusão** não funcionava devido à propagação de eventos
- **Reatividade do useToast** retornava valor ao invés de ref
- **Verificações de campos opcionais** no frontend
- **Funções duplicadas** em AnalysisDetail.vue
- **Ambiente virtual** com problemas de dependências
- **Erro de upload** com campo 'info' ausente no banco
- **Duplicação de área de resultados** removida

### Removido
- **Código duplicado** em múltiplos componentes
- **Dependências desnecessárias** do requirements.txt
- **Arquivos de documentação** redundantes e espalhados
- **Funções vazias** e código morto

### Segurança
- **Validação rigorosa** de uploads de arquivo
- **Sanitização de inputs** no frontend
- **Gerenciamento seguro** de chaves de API
- **CORS configurado** adequadamente

## [1.0.0] - 2025-09-15

### Adicionado
- **Versão inicial** da plataforma
- **Backend FastAPI** com endpoints básicos
- **Frontend Vue.js 3** com TypeScript
- **Integração com Google Gemini** para análise de imagens
- **Sistema de upload** de imagens de mamografia
- **Banco de dados SQLite** para armazenamento
- **Interface básica** para visualização de resultados
- **Docker Compose** para containerização
- **Scripts de instalação** para Rocky Linux

### Funcionalidades Iniciais
- Upload de imagens de mamografia
- Análise com Google Gemini
- Visualização de resultados em texto
- Lista de análises realizadas
- Exclusão de análises
- Health check da API

## Histórico de Decisões Técnicas Importantes

### Sistema Híbrido de IA (v2.0.0)
**Decisão**: Implementar sistema com três camadas de análise
**Contexto**: Necessidade de robustez e sempre retornar análise útil
**Impacto**: Sistema nunca falha, adequado para ambiente acadêmico

### Classificação BI-RADS (v2.0.0)
**Decisão**: Integrar classificação BI-RADS no prompt
**Contexto**: Padrão médico reconhecido internacionalmente
**Impacto**: Análises mais profissionais e clinicamente relevantes

### Design System (v2.0.0)
**Decisão**: Implementar design system baseado em CSS variables
**Contexto**: Necessidade de consistência visual e manutenibilidade
**Impacto**: Interface profissional e fácil manutenção

### Clean Architecture (v2.0.0)
**Decisão**: Seguir princípios de Clean Architecture
**Contexto**: Melhorar manutenibilidade e testabilidade
**Impacto**: Código mais organizado e fácil de manter

### Sistema de Fallback (v2.0.0)
**Decisão**: Implementar análise local OpenCV como fallback
**Contexto**: APIs externas podem falhar
**Impacto**: Sistema robusto que sempre funciona

## Breaking Changes

### v2.0.0
- **Campo `info` adicionado** ao modelo Analysis
- **Migração de banco** necessária para versões anteriores
- **Estrutura de resposta da API** alterada para incluir metadados
- **Interface do frontend** completamente reformulada

## Deprecações

### v2.0.0
- **Análise simples** sem estrutura Markdown (substituída por análise estruturada)
- **Interface básica** (substituída por design system moderno)
- **Sistema de análise único** (substituído por sistema híbrido)

## Notas de Migração

### v1.0.0 → v2.0.0

#### Backend
```bash
# Executar migração do banco
cd Backend
python migrate_database.py

# Ou migração manual
sqlite3 mamografia_analysis.db "ALTER TABLE analyses ADD COLUMN info TEXT;"
```

#### Frontend
```bash
# Atualizar dependências
cd frontend
npm install

# Instalar nova dependência
npm install marked @types/marked
```

#### Configuração
- Adicionar campo `info` nas respostas da API
- Atualizar interface TypeScript para incluir metadados
- Configurar renderização Markdown no frontend

## Roadmap Futuro

### v2.1.0 (Planejado)
- [ ] Integração com mais modelos médicos especializados
- [ ] Sistema de comparação lado a lado aprimorado
- [ ] Exportação de relatórios em PDF
- [ ] Dashboard de estatísticas avançado
- [ ] Sistema de anotações na imagem

### v2.2.0 (Planejado)
- [ ] Integração com PACS
- [ ] Sistema de usuários e permissões
- [ ] Histórico de versões de análises
- [ ] API de webhooks para integrações
- [ ] Suporte a múltiplos idiomas

### v3.0.0 (Futuro)
- [ ] Migração para PostgreSQL/MySQL
- [ ] Sistema de microserviços
- [ ] Cache distribuído (Redis)
- [ ] Processamento em background (Celery)
- [ ] WebSockets para atualizações em tempo real

## Contribuidores

### v2.0.0
- **Felipe Nascimento da Silva** - Desenvolvimento Full-Stack e arquitetura
- **Enzo Carvalho Mattiotti dos Reis** - Desenvolvimento Backend
- **João Pedro Carvalho** - Desenvolvimento Frontend

### v1.0.0
- **Felipe Nascimento da Silva** - Desenvolvimento inicial
- **Enzo Carvalho Mattiotti dos Reis** - Backend inicial
- **João Pedro Carvalho** - Frontend inicial

## Links Úteis

- [Repositório GitHub](https://github.com/Felipensct/mamografia-ia-analysis)
- [Documentação da API](http://localhost:8000/docs)
- [Guia de Desenvolvimento](./DEVELOPMENT.md)
- [Guia de Deploy](./DEPLOYMENT.md)
- [Arquitetura do Sistema](./ARCHITECTURE.md)

---

**Nota**: Este changelog segue o padrão [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e [Versionamento Semântico](https://semver.org/lang/pt-BR/).

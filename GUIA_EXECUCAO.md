# 🚀 Guia de Execução - Plataforma Mamografia IA

## 📋 Resumo das Melhorias Implementadas

### ✅ Correções Realizadas

1. **Frontend - Bugs Corrigidos:**
   - ✅ Removidas funções duplicadas em `AnalysisDetail.vue`
   - ✅ Corrigida reatividade do `useToast.ts`
   - ✅ Adicionadas verificações de campos opcionais (`info`)
   
2. **Backend - Banco de Dados:**
   - ✅ Adicionado campo `info` no modelo Analysis
   - ✅ Implementado armazenamento de metadados de processamento
   - ✅ Endpoint atualizado para retornar informações de redimensionamento

3. **IA - Prompt Otimizado:**
   - ✅ Prompt do Gemini completamente reestruturado
   - ✅ Formato Markdown estruturado
   - ✅ Classificação BI-RADS integrada
   - ✅ Priorização de achados (crítico/importante/observação)
   - ✅ Níveis de confiança e recomendações

4. **Frontend - Visualização:**
   - ✅ Biblioteca `marked` instalada
   - ✅ Renderização de Markdown implementada
   - ✅ Estilos CSS customizados para análises médicas
   - ✅ Destaque visual para achados críticos

---

## 🖥️ Como Executar o Projeto

### **Pré-requisitos:**
- Python 3.11+
- Node.js 20.19.0+
- Chaves de API:
  - Google Gemini API Key
  - Hugging Face API Key (opcional)

---

### **Opção 1: Execução em Desenvolvimento (Recomendado)**

#### **Terminal 1 - Backend:**

```bash
# Navegar para o diretório do backend
cd /home/felipe/Univap/ProjetosIV/Backend

# Criar ambiente virtual (se não existir)
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar/atualizar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp env.example .env

# Editar .env com suas chaves de API
nano .env
# ou
code .env

# IMPORTANTE: Adicione suas chaves:
# GEMINI_API_KEY=sua_chave_aqui
# HUGGINGFACE_API_KEY=sua_chave_aqui

# ⚠️ MIGRAÇÃO DO BANCO DE DADOS
# Como adicionamos o campo 'info', você tem 2 opções:

# Opção A: Deletar banco existente (perde dados)
rm mamografia_analysis.db

# Opção B: Manter dados existentes (recomendado)
# O SQLAlchemy criará automaticamente a nova coluna
# Análises antigas terão info=NULL (funciona normalmente)

# Executar backend
python3 app.py
```

**Saída esperada:**
```
🚀 Iniciando aplicação FastAPI...
📁 Upload dir: /home/felipe/Univap/ProjetosIV/Backend/uploads
📁 Results dir: /home/felipe/Univap/ProjetosIV/Backend/results
🌐 Acesse: http://localhost:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

#### **Terminal 2 - Frontend:**

```bash
# Navegar para o diretório do frontend
cd /home/felipe/Univap/ProjetosIV/frontend

# Instalar dependências (se necessário)
npm install

# Executar frontend em modo desenvolvimento
npm run dev
```

**Saída esperada:**
```
  VITE v7.1.7  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

#### **Acessar a Aplicação:**
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

### **Opção 2: Execução com Docker Compose**

```bash
# Navegar para o diretório raiz
cd /home/felipe/Univap/ProjetosIV

# Configurar variáveis de ambiente
cp env.example .env
nano .env

# Adicionar chaves de API no .env:
# GEMINI_API_KEY=sua_chave_aqui
# HUGGINGFACE_API_KEY=sua_chave_aqui
# VITE_API_URL=http://localhost:8000

# ⚠️ Se estiver migrando, remova o banco antigo:
rm Backend/mamografia_analysis.db

# Executar com Docker
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar containers
docker-compose down
```

---

## 🧪 Testando as Melhorias

### **1. Testar Upload e Processamento:**

1. Acesse http://localhost:5173
2. Faça upload de uma imagem de mamografia
3. Verifique se aparece a mensagem de sucesso (Toast)
4. Confira se mostra informações de redimensionamento (se aplicável)

### **2. Testar Análise com IA (Novo Prompt):**

1. Clique em "Analisar" em uma imagem enviada
2. Aguarde o processamento (pode levar até 2 minutos)
3. Verifique a análise estruturada em Markdown com:
   - Seções numeradas e organizadas
   - Classificação BI-RADS
   - Achados prioritários (🔴🟡🟢)
   - Níveis de confiança
   - Recomendações específicas

### **3. Testar Visualização Markdown:**

A análise deve aparecer formatada com:
- ✅ Cabeçalhos coloridos e bem estruturados
- ✅ Listas organizadas
- ✅ Destaque visual para achados críticos (vermelho)
- ✅ Destaque para achados importantes (amarelo)
- ✅ Destaque para observações gerais (verde)
- ✅ Checkboxes para recomendações

### **4. Testar Funcionalidades Existentes:**

- ✅ Visualizar detalhes de uma análise
- ✅ Excluir análise
- ✅ Copiar análise para área de transferência
- ✅ Baixar análise como TXT
- ✅ Ver lista de todas as análises
- ✅ Filtrar por status

---

## 🔍 Verificação de Problemas

### **Backend não inicia:**

```bash
# Verificar se porta 8000 está em uso
sudo lsof -ti:8000

# Se estiver, matar processo
sudo lsof -ti:8000 | xargs sudo kill -9

# Verificar chaves de API
cat Backend/.env | grep API_KEY

# Ver logs detalhados
cd Backend
python3 app.py
```

### **Frontend não inicia:**

```bash
# Verificar se porta 5173 está em uso
sudo lsof -ti:5173 | xargs sudo kill -9

# Reinstalar dependências
cd frontend
rm -rf node_modules package-lock.json
npm install

# Verificar configuração de API
cat .env.local
# ou verificar em vite.config.ts
```

### **Erro na análise de IA:**

```bash
# Verificar se a chave do Gemini está correta
# Acesse: https://makersuite.google.com/app/apikey

# Testar diretamente
curl -X POST "http://localhost:8000/api/v1/analyze/1"

# Ver logs do backend
tail -f Backend/logs.log
```

### **Erro: "table analyses has no column named info"**

**Causa:** O banco de dados não possui a coluna `info` adicionada na v2.0.0

**Solução Automática:**
```bash
cd Backend
python3 migrate_database.py
```

**Solução Manual:**
```bash
# Adicionar coluna manualmente
sqlite3 Backend/mamografia_analysis.db "ALTER TABLE analyses ADD COLUMN info TEXT;"

# Verificar se funcionou
sqlite3 Backend/mamografia_analysis.db ".schema analyses"
```

**Verificar Status:**
```bash
cd Backend
python3 migrate_database.py status
```

**Se não resolver:**
```bash
# Deletar banco e recriar (perde dados)
cd Backend
rm mamografia_analysis.db
python3 app.py
```

---

## 📊 Arquitetura Atualizada

```
Backend/
├── app.py                     # API principal (campo 'info' adicionado)
├── services/
│   ├── ai_service.py          # Prompt otimizado do Gemini
│   └── multi_ai_service.py    # Multi-IA (não integrado)
└── mamografia_analysis.db     # SQLite (nova coluna 'info')

frontend/
├── src/
│   ├── components/
│   │   ├── AnalysisDetail.vue # Renderização Markdown
│   │   └── ...
│   ├── composables/
│   │   └── useToast.ts        # Reatividade corrigida
│   ├── services/
│   │   └── api.ts             # Interface 'info' adicionada
│   └── style.css              # Estilos Markdown médico
└── package.json               # marked + @types/marked
```

---

## 🎯 Próximos Passos (Opcional)

1. **Integração Multi-IA:**
   - Criar endpoint `/api/v1/analyze-multi/{id}`
   - Interface de comparação lado a lado

2. **Melhorias Adicionais:**
   - Export para PDF com formatação
   - Gráficos e visualizações
   - Histórico de versões de análises
   - Sistema de anotações na imagem

3. **Otimizações:**
   - Cache de análises
   - Processamento em background (Celery)
   - Websockets para status em tempo real

---

## 📝 Notas Importantes

- **Banco de Dados:** O campo `info` foi adicionado mas é opcional. Análises antigas continuarão funcionando.
- **Prompt Melhorado:** As novas análises terão formato Markdown estruturado com BI-RADS.
- **Performance:** A análise pode levar mais tempo devido ao prompt mais detalhado.
- **Custo:** Prompt maior = mais tokens = possível aumento no custo da API Gemini.

---

## 🆘 Suporte

- **Email:** felipe.nascimento@univap.br
- **GitHub Issues:** Criar issue no repositório
- **Documentação API:** http://localhost:8000/docs

---

**✨ Melhorias implementadas com sucesso!**
**🎓 Projeto Mamografia IA - Projetos IV - UNIVAP 2025**


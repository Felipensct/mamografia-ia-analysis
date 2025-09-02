# 🏥 Plataforma de Análise de IAs Generativas para Mamografias

## 📋 O que é este projeto?

Esta é uma **API REST básica** desenvolvida em **FastAPI** que permite:

1. **Upload de imagens de mamografia** (PNG, JPG)
2. **Armazenamento local** de imagens enviadas
3. **Listagem** de uploads realizados
4. **API documentada** com interface Swagger

### 🎯 Objetivo
Criar a base para uma ferramenta de análise de mamografias. Esta versão inicial foca no upload e armazenamento de imagens, preparando a estrutura para futuras integrações com IA.

## 🚀 Como executar a aplicação

### 1. **Instalar dependências** (apenas uma vez)
```bash
# Executar o script de instalação
./install_system_packages.sh
```

### 2. **Executar a aplicação**
```bash
# Iniciar o servidor
python3 app.py
```

### 3. **Acessar a aplicação**
- **API**: http://localhost:8000
- **Documentação interativa**: http://localhost:8000/docs
- **Status da API**: http://localhost:8000/health

## 📁 Estrutura do projeto

```
Backend/
├── app.py                    # 🚀 Arquivo principal da aplicação
├── install_system_packages.sh # 📦 Script de instalação
├── requirements.txt          # 📋 Lista de dependências
├── env.example              # ⚙️ Exemplo de configuração
├── mamografia_analysis.db   # 🗄️ Banco de dados (não usado atualmente)
├── uploads/                 # 📁 Imagens enviadas
└── results/                 # 📁 Resultados (preparado para futuro)
```

## 🔌 Endpoints da API

### 📤 **Upload de Imagens**
```bash
POST /api/v1/upload
```
- **Função**: Enviar imagem de mamografia
- **Formato**: multipart/form-data
- **Tipos aceitos**: PNG, JPG

### 📋 **Listar Uploads**
```bash
GET /api/v1/uploads
```
- **Função**: Ver todas as imagens enviadas
- **Retorna**: Lista com informações dos arquivos

### 🔍 **Análise de Mamografia**
```bash
POST /api/v1/analyze/{filename}
```
- **Função**: Endpoint preparado para análise com IA
- **Status**: Retorna mensagem informativa (IA não implementada ainda)

### 🏥 **Status da API**
```bash
GET /health
```
- **Função**: Verificar se a API está funcionando

## 🧪 Como testar

### **Método 1: Interface Web (Recomendado)**
1. Acesse http://localhost:8000/docs
2. Clique em `POST /api/v1/upload`
3. Clique em "Try it out"
4. Selecione uma imagem
5. Clique em "Execute"

### **Método 2: cURL**
```bash
# Upload de imagem
curl -X POST "http://localhost:8000/api/v1/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sua_imagem.png"

# Listar uploads
curl http://localhost:8000/api/v1/uploads

# Verificar status
curl http://localhost:8000/health
```

## ⚙️ Configuração (Futuro)

### **Configurar APIs de IA** (Não implementado ainda)
Para futuras integrações com IA:

1. **Copiar arquivo de configuração**:
```bash
cp env.example .env
```

2. **Editar arquivo .env** (quando implementado):
```env
# Obter em: https://platform.openai.com/api-keys
OPENAI_API_KEY=sua_chave_openai_aqui

# Obter em: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=sua_chave_gemini_aqui
```

## 🛠️ Tecnologias utilizadas

- **FastAPI**: Framework web moderno e rápido
- **Uvicorn**: Servidor ASGI
- **Python**: Linguagem de programação
- **JSON**: Formato de dados da API

### 🔮 **Tecnologias planejadas** (futuras versões)
- **SQLAlchemy**: ORM para banco de dados
- **SQLite**: Banco de dados local
- **Pillow**: Processamento de imagens
- **Pydantic**: Validação de dados
- **Google Generative AI**: API do Gemini
- **OpenAI**: API do GPT-4V

## 📊 Funcionalidades implementadas

### ✅ **Funcionando agora**
- Upload de imagens de mamografia
- Validação básica de tipos de arquivo
- Armazenamento local de imagens
- API REST documentada
- Interface Swagger para testes
- Listagem de uploads realizados

### 🔄 **Preparado para implementar**
- Análise com Gemini Vision
- Análise com GPT-4V
- Comparação de resultados
- Processamento em background
- Banco de dados SQLite
- Validação avançada de imagens

## 🐛 Solução de problemas

### **Erro: "externally-managed-environment"**
✅ **Resolvido** - Use o script `install_system_packages.sh`

### **Erro: "Module not found"**
```bash
# Reinstalar dependências
sudo apt update
sudo apt install python3-fastapi python3-uvicorn python3-pil python3-sqlalchemy
```

### **Porta 8000 em uso**
```bash
# Verificar processos
sudo lsof -i :8000

# Parar processo
sudo kill -9 PID_DO_PROCESSO
```

### **Aplicação não inicia**
```bash
# Verificar se está no diretório correto
pwd
# Deve mostrar: /caminho/para/Backend

# Verificar se app.py existe
ls -la app.py
```

## 🎯 Próximos passos

1. **Testar upload** de imagens via Swagger UI
2. **Configurar chaves de API** para análise com IA
3. **Desenvolver frontend** Vue.js
4. **Implementar análise** com Gemini e GPT-4V
5. **Adicionar autenticação** e segurança

## 📞 Suporte

Se encontrar problemas:

1. **Verifique os logs** do servidor
2. **Teste endpoints básicos** primeiro
3. **Confirme dependências** instaladas
4. **Verifique permissões** de arquivo

---

## 🎉 **Resumo**

Esta é uma **API REST básica** para upload de mamografias. A aplicação está **funcionando** e pronta para receber imagens. É a base para futuras implementações de análise com IA.

**Versão atual**: MVP com upload e armazenamento
**Próxima versão**: Integração com APIs de IA

**Acesse agora**: http://localhost:8000/docs e comece a testar! 🚀
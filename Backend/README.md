# 🔧 Backend - Mamografia IA Analysis

API REST desenvolvida em FastAPI para análise de imagens de mamografia com Inteligência Artificial.

## 📋 Funcionalidades

- **Upload de imagens** de mamografia (PNG, JPG, JPEG, TIFF, BMP)
- **Análise com IA** usando Google Gemini e Hugging Face
- **Banco de dados** SQLite para armazenamento
- **API documentada** com Swagger UI
- **Processamento de imagens** com otimização automática

## 🚀 Como Executar

### **1. Instalar Dependências**
```bash
pip3 install -r requirements.txt
```

### **2. Configurar Variáveis de Ambiente**
```bash
cp env.example .env
# Editar .env com suas chaves de API
```

### **3. Executar a Aplicação**
```bash
python3 app.py
```

### **4. Acessar a API**
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Status**: http://localhost:8000/health

---

## 🔌 Endpoints da API

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

## ⚙️ Configuração

### **Arquivo .env**
```env
# Chaves de API (OBRIGATÓRIO)
GEMINI_API_KEY=your_gemini_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Configurações do Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=True
```

### **Chaves de API**
- **Google Gemini**: https://makersuite.google.com/app/apikey
- **Hugging Face**: https://huggingface.co/settings/tokens

---

## 🧪 Testes

### **Teste Manual via Swagger UI**
1. Acesse http://localhost:8000/docs
2. Teste cada endpoint individualmente
3. Faça upload de uma imagem real de mamografia
4. Execute análise e veja os resultados

### **Teste Automatizado**
```bash
python3 test_api.py
```

### **Teste via cURL**
```bash
# Upload de imagem
curl -X POST "http://localhost:8000/api/v1/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sua_imagem.jpg"

# Análise
curl -X POST "http://localhost:8000/api/v1/analyze/1"

# Listar análises
curl "http://localhost:8000/api/v1/analyses"
```

---

## 🛠️ Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **Uvicorn** - Servidor ASGI
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados local
- **Pillow** - Processamento de imagens
- **Google Generative AI** - API do Gemini
- **Hugging Face** - API de modelos de IA
- **Python-dotenv** - Gerenciamento de variáveis de ambiente

---

## 📁 Estrutura do Projeto

```
Backend/
├── app.py                    # 🚀 Aplicação principal
├── services/
│   └── ai_service.py         # 🤖 Integração com APIs de IA
├── uploads/                  # 📁 Imagens enviadas
├── results/                  # 📁 Resultados das análises
├── requirements.txt          # 📋 Dependências Python
├── env.example              # ⚙️ Exemplo de configuração
├── test_api.py              # 🧪 Testes da API
└── README.md                # 📖 Este arquivo
```

---

## 🐛 Solução de Problemas

### **Erro: "Address already in use"**
```bash
sudo lsof -i :8000
sudo kill -9 PID_DO_PROCESSO
```

### **Erro: "Module not found"**
```bash
pip3 install -r requirements.txt
```

### **Erro: "API Key not found"**
```bash
# Verificar se o arquivo .env existe
ls -la .env
cat .env
```

### **Erro: "Análise falhou"**
- Verifique suas chaves de API
- Confirme se tem créditos/quota disponível
- Verifique a conexão com a internet

---

## 📊 Funcionalidades Implementadas

### ✅ **Funcionando**
- Upload de imagens de mamografia
- Validação de tipos de arquivo
- Armazenamento local de imagens
- API REST documentada
- Interface Swagger para testes
- Análise com Google Gemini
- Fallback para Hugging Face
- Banco de dados SQLite
- Processamento de imagens otimizado

---

## 🎯 Próximos Passos

1. **Testar upload** de imagens via Swagger UI
2. **Configurar chaves de API** para análise com IA
3. **Integrar com frontend** Vue.js
4. **Adicionar autenticação** e segurança
5. **Implementar processamento em background**

---

## 📞 Suporte

Se encontrar problemas:

1. **Verifique os logs** do servidor
2. **Teste endpoints básicos** primeiro
3. **Confirme dependências** instaladas
4. **Verifique permissões** de arquivo

---

## 🎉 Resumo

Esta é uma **API REST completa** para análise de mamografias com IA. A aplicação está **100% funcional** e pronta para:

- ✅ Fazer upload de imagens
- ✅ Analisar com IA usando Gemini e Hugging Face
- ✅ Armazenar resultados no banco de dados
- ✅ Listar e consultar análises anteriores

**Acesse agora**: http://localhost:8000/docs e comece a testar! 🚀
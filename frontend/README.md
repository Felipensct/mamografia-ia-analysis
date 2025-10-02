# 🎨 Frontend - Mamografia IA Analysis

Interface moderna e intuitiva para análise de imagens de mamografia com inteligência artificial.

## 🚀 Tecnologias

- **Vue 3** - Framework JavaScript reativo
- **TypeScript** - Tipagem estática
- **Pinia** - Gerenciamento de estado
- **Vue Router** - Roteamento
- **Axios** - Cliente HTTP
- **Vite** - Build tool moderno

## 🚀 Como Executar

### **1. Instalar Dependências**
```bash
npm install
```

### **2. Executar em Desenvolvimento**
```bash
npm run dev
```

### **3. Build para Produção**
```bash
npm run build
```

### **4. Acessar a Aplicação**
- **Desenvolvimento**: http://localhost:5173
- **Produção**: http://localhost:8000 (com nginx)

---

## 🎨 Funcionalidades

- **Upload de Imagens**: Drag & drop com validação
- **Lista de Análises**: Visualização de todas as análises
- **Detalhes da Análise**: Visualização completa dos resultados
- **Status em Tempo Real**: Acompanhamento do progresso
- **Interface Responsiva**: Funciona em desktop e mobile
- **Animações Suaves**: Transições e feedback visual

---

## 📁 Estrutura do Projeto

```
frontend/
├── src/
│   ├── components/          # Componentes reutilizáveis
│   │   ├── ImageUpload.vue  # Upload de imagens
│   │   ├── AnalysisList.vue # Lista de análises
│   │   └── AnalysisDetail.vue # Detalhes da análise
│   ├── views/               # Páginas da aplicação
│   │   ├── HomeView.vue     # Página inicial
│   │   ├── AnalysesView.vue # Lista de análises
│   │   └── AnalysisDetailView.vue # Detalhes
│   ├── stores/              # Gerenciamento de estado
│   │   └── analysis.ts      # Store das análises
│   ├── services/            # Serviços externos
│   │   └── api.ts          # API do backend
│   ├── config/              # Configurações
│   │   └── api.ts          # Config da API
│   └── style.css           # Estilos globais
├── package.json            # Dependências
└── README.md              # Este arquivo
```

---

## 🔧 Configuração

### **API Backend**
O frontend se conecta ao backend através da variável `VITE_API_URL`. Por padrão, aponta para `http://localhost:8000`.

### **Gerenciamento de Estado**
O estado da aplicação é gerenciado pelo Pinia:
- `useAnalysisStore`: Gerencia análises, uploads e resultados

---

## 🎯 Componentes Principais

### **ImageUpload**
- Upload por drag & drop ou clique
- Validação de tipo e tamanho
- Preview da imagem
- Barra de progresso

### **AnalysisList**
- Lista paginada de análises
- Filtros por status
- Estatísticas em tempo real
- Ações rápidas

### **AnalysisDetail**
- Visualização da imagem original
- Resultados da análise de IA
- Ações de exportação
- Histórico de processamento

---

## 🔗 Integração com Backend

O frontend se comunica com o backend através de endpoints REST:

- `POST /api/v1/upload` - Upload de imagem
- `GET /api/v1/analyses` - Listar análises
- `GET /api/v1/analysis/{id}` - Detalhes da análise
- `POST /api/v1/analyze/{id}` - Analisar imagem

---

## 📱 Responsividade

O frontend é totalmente responsivo e funciona em:
- **Desktop**: Layout em grid com sidebar
- **Tablet**: Layout adaptativo
- **Mobile**: Layout em coluna única

---

## 🧪 Testes

### **Teste Manual**
1. Acesse http://localhost:5173
2. Faça upload de uma imagem
3. Execute a análise
4. Visualize os resultados

### **Teste Automatizado**
```bash
npm run test
```

---

## 🐛 Solução de Problemas

### **Erro de CORS**
Verifique se o backend está configurado para aceitar requisições do frontend.

### **Erro de Conexão**
Confirme se a variável `VITE_API_URL` está correta e se o backend está rodando.

### **Erro de Build**
Execute `npm run build` para ver erros detalhados.

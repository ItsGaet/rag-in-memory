# 🚀 RAG v2 - Enhanced Architecture

## 📋 Overview

**RAG v2** è una versione completamente riprogettata con focus su:
- ✨ **UI/UX Moderna** - Interfaccia intuitiva e professionale
- 🗄️ **PostgreSQL** - Persistenza dati e chat history
- 📊 **Dashboard Analytics** - Statistiche uso e performance
- 🔄 **Chat History** - Conversazioni memorizzate e recuperabili
- 📁 **Multi-Document** - Gestione batch di PDF
- ⚡ **Performance** - Caching e ottimizzazioni

## 🏗️ Stack Tecnologico

### Frontend
- **Streamlit** - Framework UI moderna
- **Streamlit-extras** - Componenti avanzati
- **Plotly** - Grafici interattivi
- **Custom CSS** - Styling professionale

### Backend
- **PostgreSQL** - Database persistente
- **SQLAlchemy** - ORM
- **LangChain** - RAG orchestration
- **FAISS** - Vector database in-memory
- **OpenAI API** - Language model

### Utilities
- **python-dotenv** - Configuration
- **Pydantic** - Data validation
- **Logging** - Application logging

## 📁 Struttura Directory

```
rag-in-memory-v2/
├── app/
│   ├── pages/
│   │   ├── 📄 1_📚_Upload_Documenti.py
│   │   ├── 💬_Chat.py
│   │   └── 📊_Analytics.py
│   ├── components/
│   │   ├── sidebar.py
│   │   ├── chat_ui.py
│   │   ├── stats_cards.py
│   │   └── upload_manager.py
│   ├── utils/
│   │   ├── pdf_processor.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── database.py
│   │   └── formatting.py
│   ├── styles/
│   │   └── custom.css
│   ├── app.py
│   └── config.py
├── database/
│   ├── models.py
│   ├── crud.py
│   └── init_db.py
├── tests/
│   ├── test_pdf_processor.py
│   ├── test_embeddings.py
│   └── test_rag_engine.py
├── requirements.txt
├── .env.example
└── docker-compose.yml
```

## 🎯 Features Principali

### 1. **Upload & Document Management**
- ✅ Upload multipli simultanei
- ✅ Preview documenti
- ✅ Gestione documenti (delete, rename)
- ✅ Status processing in tempo reale

### 2. **Chat Interface**
- ✅ Chat history persistente
- ✅ Session management
- ✅ Message formatting (code, links, tables)
- ✅ Copy-to-clipboard per risposte
- ✅ Suggested follow-up questions

### 3. **Analytics Dashboard**
- ✅ Documents statistics
- ✅ Query analytics
- ✅ Token usage tracking
- ✅ Performance metrics
- ✅ Cost estimation

### 4. **Database Schema**
```sql
-- Documents
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    file_path VARCHAR(512),
    embedding_status VARCHAR(20),
    token_count INT,
    size_bytes INT
);

-- Chat Sessions
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    document_ids INTEGER[],
    last_activity TIMESTAMP
);

-- Messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    role VARCHAR(20),
    content TEXT,
    tokens_used INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Query Analytics
CREATE TABLE queries (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    query TEXT,
    response_time_ms INT,
    tokens_used INT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🎨 UI/UX Enhancements

### Color Scheme
- Primary: `#0066FF` (Blue)
- Secondary: `#FF6B6B` (Red)
- Success: `#51CF66` (Green)
- Warning: `#FFD93D` (Yellow)
- Dark: `#1A1A1A`
- Light: `#F8F9FA`

### Components Hierarchy
1. **Sidebar** - Navigation + Quick Actions
2. **Header** - Title + Status Indicators
3. **Main Content** - Context-specific
4. **Footer** - Info + Feedback

## 🔄 Data Flow

```
PDF Upload
    ↓
PDF Processing (text extraction)
    ↓
Chunking & Tokenization
    ↓
Embedding Generation (OpenAI)
    ↓
FAISS Index Creation
    ↓
Metadata Storage (PostgreSQL)
    ↓
Ready for Queries
    ↓
User Query
    ↓
Vector Similarity Search (FAISS)
    ↓
Context Retrieval
    ↓
LLM Processing (OpenAI)
    ↓
Response with Citations
    ↓
Save to Chat History
```

## 📈 Performance Targets

- **PDF Processing**: < 5s per documento
- **Query Response**: < 3s average
- **Vector Search**: < 100ms
- **UI Responsiveness**: < 500ms render

## 🔐 Security Considerations

- ✅ API key in .env (never in code)
- ✅ Input validation
- ✅ File upload restrictions (PDF only, max 20MB)
- ✅ SQL injection prevention (SQLAlchemy ORM)

## 🚀 Deployment Ready

- Docker containerization
- Environment configuration
- Database initialization scripts
- Health checks

---

**Next Steps**: Iniziamo con i file core! 🎯

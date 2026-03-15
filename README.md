# RAG Document Agent 📄

> An intelligent document analysis system that uses Retrieval Augmented Generation (RAG) to answer questions about uploaded documents and web content.

**Developed by Md Kasif**

---

## 🎯 Overview

RAG Document Agent is a powerful AI application that allows users to:
- 📤 Upload documents (PDF, DOCX, Excel)
- 🌐 Provide web URLs for analysis
- ❓ Ask intelligent questions about the content
- 📊 Get AI-generated summaries
- 📚 View source documents with citations

The application uses **DeepSeek v3.2** (via NVIDIA Build API) as the language model, ensuring high-quality answers without needing expensive cloud infrastructure.

---

## ✨ Features

### 📤 Document Upload
- Upload multiple file types: PDF, DOCX, XLS
- Process web URLs (Wikipedia, documentation sites, etc.)
- Automatic text extraction and chunking
- Supports documents up to 50MB

### 🤖 Intelligent Q&A
- Ask questions in natural language
- Get contextual answers based on uploaded documents
- View source citations for every answer
- Powered by DeepSeek v3.2 (state-of-the-art LLM)

### 📊 Document Summarization
- Auto-generate summaries of uploaded documents
- Extract key points and main topics
- Perfect for quick document overview

### 🔍 Smart Retrieval
- Uses HuggingFace embeddings for semantic search
- Chroma vector database for fast similarity matching
- Returns top 5 most relevant chunks per query

---

## 🛠️ Tech Stack

### **LLM & AI**
- **DeepSeek v3.2** - State-of-the-art language model
  - 685B sparse mixture of experts
  - 128K context window
  - Via NVIDIA Build API (Free!)

### **Vector Database & Embeddings**
- **Chroma** - Local vector database
  - No cloud dependencies
  - Persistent storage
  - Fast similarity search
  
- **HuggingFace Sentence Transformers** - Embedding model
  - `all-MiniLM-L6-v2`
  - Free, no API key needed
  - ~120M parameters, optimized for semantic search

### **Document Processing**
- **LangChain** - LLM framework
  - RetrievalQA chains
  - Document loaders and splitters
  
- **PyPDF** - PDF extraction
- **python-docx** - Word document processing
- **openpyxl** - Excel file handling
- **BeautifulSoup** - Web scraping

### **Frontend**
- **Streamlit** - Web UI framework
  - Interactive components
  - File upload handling
  - Real-time updates

### **Infrastructure**
- **AWS EC2** - Cloud compute
  - t3.small instance
  - 2 vCPU, 2GB RAM
  - Cost: ~$5-7/month

---

## 📊 Architecture & Data Flow

### **System Architecture**
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (Streamlit)                │
│  ┌──────────────────┬──────────────────┬──────────────────┐ │
│  │ 📤 Upload Docs   │ ❓ Ask Questions │ 📊 Get Summary   │ │
│  └──────────────────┴──────────────────┴──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│              Document Processing Layer (LangChain)           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Load Files   │  │ Load URLs    │  │ Chunk Text   │      │
│  │ (PyPDF,      │  │ (WebBase     │  │ (RecursiveCS │      │
│  │  python-docx)│  │  Loader)     │  │  TextSplit)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│              Embedding & Storage Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ HuggingFace Sentence Transformers                    │   │
│  │ (all-MiniLM-L6-v2) - Generate embeddings             │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Chroma Vector Database (Local)                       │   │
│  │ Store: [embedding, text, metadata]                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│              RAG Agent Layer                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Retrieve top-5 relevant chunks from Chroma        │   │
│  │ 2. Create context from retrieved chunks              │   │
│  │ 3. Send [context + question] to DeepSeek             │   │
│  │ 4. Return answer + source citations                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│              LLM Layer (DeepSeek v3.2)                       │
│  Via NVIDIA Build API                                        │
│  - Process natural language                                  │
│  - Generate contextual answers                               │
│  - High quality responses                                    │
└─────────────────────────────────────────────────────────────┘
---

## 🔄 Complete Application Flow

### **Flow 1: Document Upload & Indexing**
User uploads documents/URLs
│
▼
DocumentProcessor.process_mixed()
│
├─ For files:
│  └─ load_file() → load_pdf/docx/excel()
│
├─ For URLs:
│  └─ load_web_urls() → WebBaseLoader
│
▼
chunk_documents()
│
└─ RecursiveCharacterTextSplitter
(chunk_size=1000, overlap=200)
│
▼
VectorStore.add_documents()
│
├─ HuggingFaceEmbeddings.embed()
│  └─ Generate vector for each chunk
│
├─ Chroma.from_documents()
│  └─ Store vectors locally
│
▼
✅ Documents indexed and ready for querying
**Time:** 30-60 seconds per 100 chunks

---

### **Flow 2: Question Answering (RAG)**
User asks question
│
▼
RAGAgent.analyze_documents()
│
├─ VectorStore.search(query, k=5)
│  │
│  ├─ Convert question to embedding
│  │
│  ├─ Find top-5 similar chunks in Chroma
│  │
│  └─ Extract: [text, metadata]
│
▼
setup_qa_chain()
│
├─ Create PromptTemplate:
│  "Use context to answer question"
│
├─ Create RetrievalQA chain
│  └─ Combines retriever + LLM
│
▼
RetrievalQA.invoke()
│
├─ Build prompt: [retrieved_context + question]
│
├─ Send to DeepSeek API
│  └─ NVIDIA Build endpoint
│
▼
DeepSeek generates answer
│
├─ Reads context
├─ Understands question
├─ Generates relevant response
│
▼
Extract & format response
│
├─ Get answer text
├─ Get source documents
├─ Format metadata
│
▼
Display to user
│
├─ 💡 Answer (main response)
├─ 📚 Source Documents (top-5 chunks)
│
▼
✅ Question answered with citations
**Time:** 1-2 minutes (includes API latency)

---

### **Flow 3: Document Summarization**
User clicks "Generate Summary"
│
▼
RAGAgent.get_summary()
│
├─ VectorStore.search("summary overview main points", k=5)
│  └─ Get top-5 relevant chunks
│
├─ Combine chunks:
│  └─ combined_text = chunk1 + chunk2 + ... + chunk5
│
▼
Create summary prompt
│
├─ "Provide concise summary of:"
├─ [combined_text]
│
▼
Send to DeepSeek
│
├─ Process combined text
├─ Extract key points
├─ Generate concise summary
│
▼
Display summary to user
│
└─ 📋 Summary (AI-generated overview)
│
▼
✅ Summary displayed
**Time:** 1-2 minutes

---

## 📁 Project Structure
rag-document-agent/
│
├── src/                          # Source code
│   ├── agents/
│   │   ├── init.py
│   │   └── rag_agent.py         # Main RAG agent logic
│   │
│   ├── tools/
│   │   ├── init.py
│   │   ├── document_loader.py   # Load & chunk documents
│   │   └── embeddings.py        # Chroma vector DB
│   │
│   └── config/
│       ├── init.py
│       └── settings.py          # Configuration
│
├── app.py                        # Streamlit frontend
├── requirements.txt              # Python dependencies
├── .env                         # Environment variables
├── .gitignore                   # Git ignore rules
│
├── uploads/                      # User uploaded files
├── chroma_db/                    # Vector database (created automatically)
├── logs/                         # Application logs
│
└── README.md                     # This file
---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.11+
- AWS EC2 instance (or local machine)
- NVIDIA Build API key (free)
- ~500MB disk space

### **Installation**

```bash
# 1. Clone repository
git clone https://github.com/yourusername/rag-document-agent.git
cd rag-document-agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env and add your NVIDIA_API_KEY

# 5. Run application
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Access Application
Open browser: http://localhost:8501 or http://YOUR_IP:8501

💡 How It Works: Technical Details
1. Document Chunking
# Text is split into overlapping chunks
chunk_size = 1000          # characters
chunk_overlap = 200        # characters

Example:
Text: "Document content... [1000 chars] ...more content [1000 chars]"
       └─ Chunk 1: chars 0-1000
       └─ Chunk 2: chars 800-1800  (200 char overlap)
       └─ Chunk 3: chars 1600-2600
2. Embedding Generation
# HuggingFace converts text to vectors
Model: sentence-transformers/all-MiniLM-L6-v2
Output: 384-dimensional vector per chunk

Example:
Text: "What is machine learning?"
  │
  ▼
[0.234, -0.456, 0.789, ..., 0.123]  # 384 numbers
3. Vector Similarity Search
# Chroma finds most similar chunks
Question: "How does machine learning work?"
Question vector: [0.245, -0.467, 0.801, ...]

Compare with all chunk vectors:
  Chunk 1: 0.98 similarity ← Retrieved!
  Chunk 2: 0.95 similarity ← Retrieved!
  Chunk 3: 0.92 similarity ← Retrieved!
  Chunk 4: 0.45 similarity ✗ Not similar
  Chunk 5: 0.38 similarity ✗ Not similar

Return: Top-5 chunks
4. RAG (Retrieval Augmented Generation)
# DeepSeek receives context + question
Prompt: """
Context:
[Retrieved chunks 1-5]

Question: How does machine learning work?

Answer: [DeepSeek generates answer based on context]
"""
🔑 Key Components
RAGAgent (src/agents/rag_agent.py)
Purpose: Main orchestration logic
Methods:
__init__() - Initialize LLM and vector store
setup_qa_chain() - Create RAG chain
analyze_documents() - Answer questions
get_summary() - Summarize documents
DocumentProcessor (src/tools/document_loader.py)
Purpose: Load and process documents
Supports:
PDF files (PyPDF)
DOCX files (python-docx)
Excel files (openpyxl)
Web URLs (BeautifulSoup)
VectorStore (src/tools/embeddings.py)
Purpose: Manage embeddings and vector search
Features:
HuggingFace embeddings (no API key!)
Chroma local database
Similarity search
Streamlit App (app.py)
Purpose: Web interface
Features:
File upload
URL input
Q&A interface
Summary generation
⚙️ Configuration
Edit .env file:
# NVIDIA Build API
NVIDIA_API_KEY=nvapi_your_key_here

# Document Processing
CHUNK_SIZE=1000              # Characters per chunk
CHUNK_OVERLAP=200            # Overlap between chunks
MAX_FILE_SIZE_MB=50          # Max file size

# Logging
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR
🎯 Use Cases
1. Research Documentation
Upload: Kubernetes documentation
Ask: "How do I deploy applications?"
Get: Detailed answer with source links
2. PDF Analysis
Upload: Company financial report (PDF)
Ask: "What is the revenue for 2023?"
Get: Specific answer with page references
3. Web Content Analysis
Provide: Wikipedia articles (URLs)
Ask: "What are key historical events?"
Get: Comprehensive summary
4. Multi-Document Analysis
Upload: Multiple PDFs + URLs
Ask: "Compare these two approaches"
Get: Comparative analysis with citations
📊 Performance Metrics
Metric	Value	Notes
Document Upload	30-60 sec	100 chunks
First Answer	1-2 min	DeepSeek API latency
Subsequent Answers	30-60 sec	Cached embeddings
Summary Generation	1-2 min	5-chunk summary
Max Document Size	50 MB	Configurable
Vector Search	<100 ms	Chroma speed
Embedding Size	384D	HuggingFace model
🔐 Security
✅ API keys stored in .env (not in code)
✅ .env is in .gitignore (not pushed to GitHub)
✅ Local vector database (no cloud data exposure)
✅ No user data stored on servers
✅ HTTPS encryption (when deployed with HTTPS)
🐛 Troubleshooting
Q: Getting API 404 error
A: Check model name in .env is correct:
NVIDIA_MODEL = "deepseek-ai/deepseek-v3.2"
Q: Documents not loading
A: Check file formats (PDF, DOCX, XLS) and ensure file size < 50MB

Q: Slow responses
A: Normal! First run downloads HuggingFace model (~200MB). Subsequent runs are faster.

Q: Out of memory
A: Try smaller CHUNK_SIZE or process fewer documents at once
🚀 Deployment
Local Machine
streamlit run app.py
# Access: http://localhost:8501
AWS EC2
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
# Access: http://YOUR_IP:8501
Docker (Optional)
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py"]
📈 Future Enhancements
 Multi-user support with session management
 Document comparison features
 Export results as PDF
 Custom prompt templates
 Integration with cloud storage (S3, Google Drive)
 Real-time collaboration
 Advanced analytics dashboard
 Caching for repeated queries
📝 License
This project is open source and available under the MIT License.

👤 Author
Developed by Md Kasif

GitHub: [your-github-username]
LinkedIn: [your-linkedin]
Email: [your-email]
🙏 Acknowledgments
DeepSeek team for excellent LLM
NVIDIA for Build API
LangChain community
Streamlit team
HuggingFace for embedding models
❓ Support
For issues, questions, or suggestions:

Open an issue on GitHub
Check existing documentation
Review troubleshooting section
Happy documenting! 🎉

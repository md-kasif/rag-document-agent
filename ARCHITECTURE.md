
RAG Document Agent uses a modern stack combining LangChain, DeepSeek AI, and local vector storage.
User Input
↓
Document Processing (LangChain)
↓
Vector Embeddings (HuggingFace)
↓
Local Storage (Chroma)
↓
RAG Retrieval
↓
DeepSeek LLM
↓
Response to User
---

## Architecture Layers

### 1. **User Interface Layer** 🎨
- **Framework**: Streamlit
- **Features**:
  - File upload (PDF, DOCX, XLS)
  - URL input
  - Question input
  - Real-time results display
  - Source citations

### 2. **Document Processing Layer** 📄
- **PyPDFLoader**: Extract text from PDFs
- **Docx2txtLoader**: Extract from Word docs
- **UnstructuredExcelLoader**: Extract from Excel
- **WebBaseLoader**: Load web content
- **RecursiveCharacterTextSplitter**: Split into chunks
  - Chunk size: 1000 characters
  - Overlap: 200 characters

### 3. **Embedding & Vector Storage Layer** 🔍
- **HuggingFace Embeddings**
  - Model: `sentence-transformers/all-MiniLM-L6-v2`
  - Dimensions: 384
  - Speed: ~1000 tokens/sec
  - Cost: FREE

- **Chroma Vector DB**
  - Local persistent storage
  - Sub-100ms search time
  - No API keys needed

### 4. **RAG Orchestration Layer** 🤖
- **LangChain RetrievalQA**
- **Query → Retrieve → Generate** workflow
- Top-5 document retrieval
- Context-aware prompting

### 5. **LLM Layer** 🧠
- **DeepSeek v3.2**
- Via NVIDIA Build API
- 685B parameters (sparse MoE)
- 128K context window
- FREE tier available

---

## Data Flow

### Document Upload Flow
User uploads file/URL
↓
DocumentProcessor loads content
↓
RecursiveCharacterTextSplitter chunks text
↓
HuggingFace generates embeddings (384D vectors)
↓
Chroma stores [vector + text + metadata]
↓
Ready for queries ✓
### Question Answering Flow
User asks question
↓
HuggingFace embeds question (384D)
↓
Chroma searches for similar chunks
↓
Retrieve top-5 most relevant chunks
↓
Build context from retrieved chunks
↓
Send [context + question] to DeepSeek
↓
DeepSeek generates answer
↓
Extract answer + sources
↓
Display to user with citations ✓
---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Web interface |
| **LLM** | DeepSeek v3.2 | AI responses |
| **LLM API** | NVIDIA Build | Free API access |
| **RAG Framework** | LangChain | Orchestration |
| **Embeddings** | HuggingFace | Vector generation |
| **Vector DB** | Chroma | Local storage |
| **Document Loading** | LangChain | File processing |
| **Deployment** | AWS EC2 | Cloud hosting |
| **Python** | 3.11 | Runtime |

---

## Component Details

### DocumentProcessor
```python
Responsibilities:
- Load documents (PDF, DOCX, XLS)
- Load web content (URLs)
- Split text into chunks
- Preserve metadata
VectorStore (Chroma)
Responsibilities:
- Store embeddings
- Search similar documents
- Manage collections
- Persist data locally
RAGAgent
Responsibilities:
- Orchestrate RAG workflow
- Call DeepSeek API
- Extract sources
- Format responses
File Structure
python
Run Code

Copy code
rag-document-agent/
├── app.py                          # Streamlit frontend
├── requirements.txt                # Dependencies
├── .env.example                    # Config template
│
├── src/
│   ├── agents/
│   │   └── rag_agent.py           # RAG orchestration
│   ├── tools/
│   │   ├── document_loader.py     # Document processing
│   │   └── embeddings.py          # Vector DB management
│   └── config/
│       └── settings.py             # Configuration
│
├── docs/
│   ├── README.md                  # Project overview
│   ├── ARCHITECTURE.md            # This file
│   ├── SETUP.md                   # Installation
│   └── CONTRIBUTING.md            # Contribution guide
│
└── Local Storage (created at runtime):
    ├── chroma_db/                 # Vector database
    ├── uploads/                   # User uploads
    └── logs/                       # Application logs
Performance Characteristics
Operation	Time	Notes
Document Upload	30-60s	100 chunks
First Question	1-2 min	DeepSeek API latency
Subsequent Questions	30-60s	Cached embeddings
Vector Search	<100ms	Chroma speed
Embedding Generation	~1s per 1000 tokens	HuggingFace CPU
Security & Privacy
✅ Protected

API keys in .env (not on GitHub)
Local vector database (no cloud)
No external data storage
HTTPS ready
❌ Exposed Risk (if misconfigured)

API tokens in code
Credentials in version control
Public repository with secrets
Deployment Options
Local Machine
bash

Copy code
streamlit run app.py
# Access: http://localhost:8501

AWS EC2
bash

Copy code
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
# Access: http://YOUR_IP:8501

Docker (Optional)
bash

Copy code
docker build -t rag-agent:latest .
docker run -p 8501:8501 -e NVIDIA_API_KEY=your_key rag-agent:latest

API Integrations
NVIDIA Build API (DeepSeek)
Endpoint: https://integrate.api.nvidia.com/v1/chat/completions
Model: deepseek-ai/deepseek-v3.2
Auth: Bearer token
Cost: FREE
HuggingFace
Model: sentence-transformers/all-MiniLM-L6-v2
Type: Sentence embeddings
Cost: FREE (local inference)
Scalability Considerations
Current Setup
✅ Single documents up to 50MB
✅ Multiple file uploads
✅ Sequential processing
✅ Local vector storage
For Production Scale
 Batch document processing
 Distributed vector search
 Cloud vector DB (Pinecone, Weaviate)
 LLM caching
 Query result caching
Future Enhancements
 Multi-user support
 Document comparison
 Custom prompts
 Export to PDF
 Real-time collaboration
 Analytics dashboard
 Advanced filtering
 Citation management
Development Notes
Code Structure
Modular design (agents, tools, config)
Type hints throughout
Comprehensive logging
Error handling
Testing
Manual testing on EC2
Sample documents included
Example queries provided
Documentation
Inline code comments
Docstrings on all functions
README with examples
This architecture guide
Resources
LangChain Documentation
DeepSeek Model
Chroma Vector DB
HuggingFace
Streamlit
AWS EC2
Developed by Md Kasif

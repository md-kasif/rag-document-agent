# System Architecture & Technical Deep Dive

## 📐 Complete System Diagram


┌────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                           │
│                          (Streamlit Web App)                           │
│                                                                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  Upload Files    │  │  Ask Questions   │  │  Get Summary     │   │
│  │  (PDF,DOCX,XLS) │  │  (Natural Lang)  │  │  (AI Generated)  │   │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘   │
│           │                     │                     │               │
└───────────┼─────────────────────┼─────────────────────┼───────────────┘
│                     │                     │
▼                     ▼                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     DOCUMENT PROCESSING LAYER                          │
│                        (LangChain Components)                          │
│                                                                        │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐      │
│  │   Document Loaders   │  │   Text Splitting & Chunking      │      │
│  │                      │  │                                  │      │
│  │ • PyPDFLoader        │  │ • RecursiveCharacterSplitter     │      │
│  │ • Docx2txtLoader     │  │   - chunk_size: 1000             │      │
│  │ • UnstructuredExcel  │  │   - chunk_overlap: 200           │      │
│  │ • WebBaseLoader      │  │   - Preserves semantic units     │      │
│  └──────────────────────┘  └──────────────────────────────────┘      │
│           │                              │                            │
│           └──────────────┬───────────────┘                            │
│                          │                                            │
│                  Document Chunks (List)                               │
│                  [chunk1, chunk2, ...]                                │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
│
▼
┌────────────────────────────────────────────────────────────────────────┐
│                     EMBEDDING & VECTOR STORE LAYER                     │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────┐        │
│  │          HuggingFace Sentence Transformers               │        │
│  │                                                           │        │
│  │  Model: sentence-transformers/all-MiniLM-L6-v2          │        │
│  │  • Parameters: ~120M                                     │        │
│  │  • Output: 384-dimensional vectors                       │        │
│  │  • Speed: ~1000 tokens/sec on CPU                        │        │
│  │  • Cost: FREE (no API key needed)                        │        │
│  └──────────────────────────────────────────────────────────┘        │
│           │                                                           │
│           ▼                                                           │
│  ┌──────────────────────────────────────────────────────────┐        │
│  │    Chroma Vector Database (Local Persistent Storage)    │        │
│  │                                                           │        │
│  │  Storage Format:                                         │        │
│  │  {                                                        │        │
│  │    "id": "chunk_123",                                    │        │
│  │    "embedding": [0.234, -0.456, ...],  # 384D            │        │
│  │    "text": "chunk content...",                           │        │
│  │    "metadata": {                                         │        │
│  │      "source": "document.pdf",                           │        │
│  │      "page": 5                                           │        │
│  │    }                                                      │        │
│  │  }                                                        │        │
│  │                                                           │        │
│  │  • Collection: "documents"                               │        │
│  │  • Persistence: ~/chroma_db/                            │        │
│  │  • Query time: <100ms per search                        │        │
│  └──────────────────────────────────────────────────────────┘        │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
│
▼
┌────────────────────────────────────────────────────────────────────────┐
│                        RAG ORCHESTRATION LAYER                         │
│                     (LangChain RAG Components)                         │
│                                                                        │
│  Step 1: RETRIEVAL                                                     │
│  ────────────────────                                                  │
│  • Convert user question to embedding (HuggingFace)                   │
│  • Search Chroma: find top-5 similar chunks                           │
│  • Retrieve [text, metadata] for each chunk                           │
│                                                                        │
│  Step 2: CONTEXT PREPARATION                                          │
│  ───────────────────────────                                          │
│  Build prompt template:                                               │
│  """                                                                   │
│  Use context to answer question.                                      │
│  If unknown, say "I don't know"                                       │
│                                                                        │
│  Context:                                                             │
│  [Retrieved chunks here]                                              │
│                                                                        │
│  Question: [User question]                                            │
│                                                                        │
│  Answer:                                                              │
│  """                                                                   │
│                                                                        │
│  Step 3: LLM INVOCATION                                               │
│  ──────────────────────                                               │
│  Send complete prompt to DeepSeek API                                 │
│                                                                        │
│  Step 4: RESPONSE PROCESSING                                          │
│  ──────────────────────────                                           │
│  • Extract answer text                                                │
│  • Extract source documents                                           │
│  • Format for display                                                 │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
│
▼
┌────────────────────────────────────────────────────────────────────────┐
│                        LLM INFERENCE LAYER                             │
│                   (NVIDIA Build API - DeepSeek v3.2)                   │
│                                                                        │
│  • Endpoint: https://integrate.api.nvidia.com/v1/chat/completions    │
│  • Model: deepseek-ai/deepseek-v3.2                                   │
│  • Architecture: Sparse Mixture of Experts (MoE)                      │
│  • Parameters: 685B (but only ~37B active per token)                  │
│  • Context Window: 128K tokens                                        │
│  • Input Format: OpenAI-compatible chat API                           │
│  • Response Time: 1-2 minutes (includes network latency)              │
│  • Cost: FREE via NVIDIA Build API                                    │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
│
▼
┌────────────────────────────────────────────────────────────────────────┐
│                    RESPONSE DELIVERY LAYER                             │
│                        (Streamlit Display)                            │
│                                                                        │
│  ┌─────────────────────────┐  ┌──────────────────────────────────┐  │
│  │  Main Answer             │  │  Source Citations                │  │
│  │  (from DeepSeek)         │  │  (with metadata)                 │  │
│  │                          │  │                                  │  │
│  │  Formatted as markdown   │  │  • Source 1: [content preview]  │  │
│  │  with line breaks        │  │  • Source 2: [content preview]  │  │
│  │  and emphasis            │  │  • Source 3: [content preview]  │  │
│  │                          │  │  • Source 4: [content preview]  │  │
│  │                          │  │  • Source 5: [content preview]  │  │
│  └─────────────────────────┘  └──────────────────────────────────┘  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘

yaml

Copy code

---

## 🔄 Data Flow Diagram

### **Upload & Indexing Flow**


User Action: Click "🚀 Process Documents"
│
├─ File Upload
│  └─ Streamlit: st.file_uploader()
│
├─ URL Input
│  └─ Streamlit: st.text_area()
│
▼
DocumentProcessor.process_mixed(files, urls)
│
├─ Process Files:
│  ├─ For .pdf: PyPDFLoader()
│  │   └─ Extract text from all pages
│  │
│  ├─ For .docx: Docx2txtLoader()
│  │   └─ Extract text from document
│  │
│  └─ For .xlsx: UnstructuredExcelLoader()
│      └─ Extract text from sheets
│
├─ Process URLs:
│  └─ WebBaseLoader()
│      └─ Fetch & parse HTML
│
▼
Document List: [Document, Document, Document, ...]
│
├─ Each Document has:
│  ├─ page_content: "text content..."
│  ├─ metadata: {"source": "file.pdf", "page": 1}
│  └─ Other fields
│
▼
RecursiveCharacterTextSplitter.split_documents()
│
├─ Algorithm:
│  ├─ Try splitting by "\n\n" (paragraphs)
│  ├─ If still too large, try "\n" (lines)
│  ├─ If still too large, try " " (words)
│  └─ If still too large, split by character
│
├─ For each chunk:
│  ├─ Size check: ~1000 characters
│  ├─ Overlap: ~200 characters with previous
│  └─ Preserve context
│
▼
Chunks List: [chunk1, chunk2, chunk3, ...]
│
▼
VectorStore.add_documents(chunks)
│
├─ For each chunk:
│  │
│  ├─ HuggingFaceEmbeddings.embed_documents()
│  │  └─ Input: chunk text
│  │  └─ Model: all-MiniLM-L6-v2
│  │  └─ Output: [384 floats] (vector)
│  │
│  └─ Store in Chroma:
│     ├─ Vector
│     ├─ Original text
│     └─ Metadata
│
▼
✅ Successfully indexed
│
└─ Storage location: ~/chroma_db/
└─ Persistent across sessions

yaml

Copy code

---

### **Question Answering Flow**


User Action: Type question & click "🔍 Search & Answer"
│
▼
RAGAgent.analyze_documents(vectorstore, question)
│
├─ Step 1: CONVERT QUESTION TO EMBEDDING
│  │
│  ├─ HuggingFaceEmbeddings.embed_query()
│  │  ├─ Input: "How do I use this?"
│  │  ├─ Model: all-MiniLM-L6-v2
│  │  └─ Output: [384 floats] (query vector)
│  │
│  └─ Store: question_vector
│
├─ Step 2: SEARCH FOR SIMILAR CHUNKS
│  │
│  ├─ Chroma.similarity_search()
│  │  ├─ Input: question_vector, k=5
│  │  ├─ Algorithm: cosine similarity search
│  │  │   └─ Find top-5 highest similarity scores
│  │  │   └─ Similarity range: 0.0 to 1.0
│  │  │   └─ Higher = more similar
│  │  └─ Output: [chunk1, chunk2, chunk3, chunk4, chunk5]
│  │
│  └─ Store: retrieved_chunks
│
├─ Step 3: BUILD CONTEXT
│  │
│  ├─ Combine all 5 chunks:
│  │  ├─ context = chunk1.text + chunk2.text + ... + chunk5.text
│  │  └─ Total length: ~5000 characters
│  │
│  └─ Store: context_text
│
├─ Step 4: SETUP QA CHAIN
│  │
│  ├─ Create PromptTemplate:
│  │  ├─ Variables: ["context", "question"]
│  │  └─ Template:
│  │     """
│  │     You are a helpful assistant analyzing documents.
│  │     Use the following context to answer the question.
│  │
│  │     Context:
│  │     {context}
│  │
│  │     Question: {question}
│  │
│  │     Answer:
│  │     """
│  │
│  ├─ Create Retriever:
│  │  └─ vectorstore.as_retriever(search_kwargs={"k": 5})
│  │
│  ├─ Create RetrievalQA Chain:
│  │  ├─ chain_type: "stuff" (stuff all docs in context)
│  │  ├─ llm: NVIDIADeepSeekLLM
│  │  ├─ retriever: from above
│  │  └─ chain_type_kwargs: {"prompt": prompt_template}
│  │
│  └─ Store: qa_chain
│
├─ Step 5: INVOKE CHAIN
│  │
│  ├─ qa_chain({"query": user_question})
│  │  ├─ Internally:
│  │  │  ├─ Retriever finds top-5 docs
│  │  │  ├─ Fill prompt with context + question
│  │  │  ├─ Send to LLM
│  │  │  └─ Get response
│  │  │
│  │  └─ Return: result dict
│  │
│  └─ Store: result
│
├─ Step 6: SEND TO DEEPSEEK API
│  │
│  ├─ NVIDIADeepSeekLLM._call()
│  │  ├─ Build HTTP request:
│  │  │  ├─ URL: https://integrate.api.nvidia.com/v1/chat/completions
│  │  │  ├─ Method: POST
│  │  │  ├─ Headers:
│  │  │  │  ├─ Authorization: Bearer {NVIDIA_API_KEY}
│  │  │  │  └─ Content-Type: application/json
│  │  │  │
│  │  │  └─ Body:
│  │  │     {
│  │  │       "model": "deepseek-ai/deepseek-v3.2",
│  │  │       "messages": [
│  │  │         {"role": "user", "content": full_prompt}
│  │  │       ],
│  │  │       "temperature": 0.1,
│  │  │       "max_tokens": 1000,
│  │  │       "top_p": 0.7
│  │  │     }
│  │  │
│  │  ├─ Send request (timeout: 120 seconds)
│  │  │
│  │  └─ Get response:
│  │     {
│  │       "choices": [
│  │         {"message": {"content": "The answer is..."}}
│  │       ]
│  │     }
│  │
│  └─ Store: answer_text = response content
│
├─ Step 7: EXTRACT SOURCES
│  │
│  ├─ From result["source_documents"]:
│  │  ├─ For each document:
│  │  │  ├─ Extract: page_content (first 300 chars)
│  │  │  ├─ Extract: metadata (source, page, etc.)
│  │  │  └─ Create: source_dict
│  │  │
│  │  └─ Create: sources_list
│  │
│  └─ Store: sources
│
├─ Step 8: FORMAT RESPONSE
│  │
│  ├─ Create response dict:
│  │  {
│  │    "answer": answer_text,
│  │    "sources": sources_list,
│  │    "success": True
│  │  }
│  │
│  └─ Store: final_result
│
▼
Return to Streamlit
│
├─ Display answer in markdown
└─ Display sources in expandable sections

✅ Question answered!

yaml

Copy code

---

### **Summary Generation Flow**


User Action: Click "📋 Generate Summary"
│
▼
RAGAgent.get_summary(vectorstore, num_chunks=5)
│
├─ Step 1: SEARCH FOR RELEVANT CHUNKS
│  │
│  ├─ Convert search query to embedding:
│  │  └─ Query: "summary overview main points"
│  │
│  ├─ Search Chroma for top-5 matches
│  │  └─ Retrieve most representative chunks
│  │
│  └─ Store: results = [chunk1, chunk2, chunk3, chunk4, chunk5]
│
├─ Step 2: COMBINE CHUNKS
│  │
│  ├─ combined_text = ""
│  ├─ For each chunk:
│  │  └─ combined_text += chunk.page_content + "\n\n"
│  │
│  └─ Result: ~5000 characters of combined text
│
├─ Step 3: CREATE SUMMARY PROMPT
│  │
│  ├─ summary_prompt = """
│  │  Provide a concise and comprehensive summary of:
│  │
│  │  {combined_text}
│  │
│  │  Summary:
│  │  """
│  │
│  └─ Store: summary_prompt
│
├─ Step 4: SEND TO DEEPSEEK
│  │
│  ├─ llm._call(summary_prompt)
│  │  └─ Same API call as above
│  │
│  └─ Store: summary_text
│
▼
Return & Display Summary
│
└─ Show in markdown format

✅ Summary generated!

python
Run Code

Copy code

---

## 🔌 API Specifications

### **NVIDIA Build API Call**

```python
import requests

def call_deepseek(prompt: str, api_key: str) -> str:
    """Call DeepSeek via NVIDIA Build API"""
    
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-ai/deepseek-v3.2",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,      # Lower = more focused/deterministic
        "max_tokens": 1000,      # Max response length
        "top_p": 0.7,            # Nucleus sampling
        "stream": False
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=120)
    
    if response.status_code == 200:
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        return answer
    else:
        raise Exception(f"API Error: {response.status_code}")


📊 Embedding Specification
HuggingFace Embeddings
less

Copy code
Model: sentence-transformers/all-MiniLM-L6-v2

Specifications:
├─ Parameters: 120M
├─ Embedding dimension: 384
├─ Max sequence length: 512 tokens
├─ Training data: SNLI, AllNLI datasets
├─ Similarity metric: Cosine similarity
└─ Speed: ~1000 tokens/sec on CPU

Example:
Input: "What is machine learning?"
Output: [0.234, -0.456, 0.789, ..., 0.123]  # 384 numbers

Similarity calculation:
cos_sim(query_embedding, doc_embedding) = dot_product / (norm1 * norm2)
Range: 0.0 (dissimilar) to 1.0 (identical)

💾 Chroma Storage Format
makefile

Copy code
Directory: ~/chroma_db/

Structure:
chroma_db/
├── documents/                    # Collection name
│   ├── index.bin                # Vector index
│   ├── data.db                  # SQLite metadata
│   └── embeddings.pkl           # Pickled embeddings
│
└── chroma.sqlite                # SQLite database

Query Response Format:
{
  "ids": ["chunk_1", "chunk_2"],
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
  "documents": ["text1", "text2"],
  "metadatas": [
    {"source": "file1.pdf", "page": 1},
    {"source": "file2.pdf", "page": 3}
  ],
  "distances": [0.15, 0.23]  # Lower = more similar
}

⚡ Performance Optimizations
1. Embedding Caching
Embeddings are computed once and stored
Same text won't be re-embedded
Saves compute and time
2. Sparse MoE (Mixture of Experts)
DeepSeek uses sparse MoE architecture
Only ~37B parameters active per token (out of 685B total)
Faster inference than dense models
3. Chunk Overlap
200-character overlap preserves context
Prevents information loss at chunk boundaries
Small overhead (only 20% extra storage)
4. Local Vector Search
Chroma runs locally on EC2
No network latency for embedding search
Sub-100ms query times
🔒 Security Considerations
API Key Management

Stored in .env file
.env in .gitignore
Not exposed in logs
Data Privacy

All data processed locally (except LLM call)
Vector DB stored locally
No cloud dependencies
Input Validation

File size limits (50MB)
File type whitelist
URL validation
🎯 System Requirements
Memory
Streaming: 300-500 MB (base system)
Processing large doc: 1-2 GB
Total: 2GB minimum (4GB recommended)
CPU
Embedding: Single-threaded CPU is fine (~1000 tokens/sec)
No GPU required
Storage
OS: 3GB
Dependencies: 2GB
Documents cache: 15-20GB
Total: 30GB recommended
Network
API calls: NVIDIA Build API
Bandwidth: ~100KB per API call (text only)
Latency: 1-2 minutes per response (acceptable)
This completes the technical architecture documentation!

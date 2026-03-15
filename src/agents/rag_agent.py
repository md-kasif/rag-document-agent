"""
RAG Agent - Main agent for document analysis
Using DeepSeek v3.2 via NVIDIA Build API + Chroma Vector DB
"""

import logging
from typing import Dict, Any
import requests
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from pydantic import Field

from src.config import NVIDIA_API_KEY, NVIDIA_MODEL
from src.tools.embeddings import VectorStore

logger = logging.getLogger(__name__)

# ============================================================================
# NVIDIA DeepSeek LLM Wrapper
# ============================================================================

class NVIDIADeepSeekLLM(LLM):
    """
    Wrapper for NVIDIA DeepSeek API
    Using NVIDIA Build API (https://build.nvidia.com/)
    """
    
    api_key: str = Field(default=NVIDIA_API_KEY)
    model: str = Field(default=NVIDIA_MODEL)
    temperature: float = Field(default=0.1)
    max_tokens: int = Field(default=1000)
    
    # Define API URL as class variable (not a Pydantic field)
    API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    class Config:
        """Pydantic config"""
        arbitrary_types_allowed = True
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM"""
        return "nvidia_deepseek"
    
    def _call(self, prompt: str, stop=None, **kwargs) -> str:
        """Call NVIDIA DeepSeek API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": 0.7,
            }
            
            logger.info(f"🔄 Calling NVIDIA DeepSeek API...")
            
            response = requests.post(
                self.API_URL,
                json=data,
                headers=headers,
                timeout=120
            )
            
            if response.status_code != 200:
                error_msg = f"API Error: {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                return f"Error: {error_msg}"
            
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            logger.info(f"✅ Got response from DeepSeek")
            
            return answer
            
        except Exception as e:
            logger.error(f"❌ Error calling NVIDIA API: {str(e)}")
            return f"Error: {str(e)}"

# ============================================================================
# RAG Agent
# ============================================================================

class RAGAgent:
    """
    RAG Agent for document analysis
    Uses DeepSeek v3.2 + Chroma Vector DB + HuggingFace Embeddings
    """
    
    def __init__(self):
        """Initialize RAG agent"""
        try:
            logger.info("🚀 Initializing RAG Agent...")
            
            # Initialize LLM
            self.llm = NVIDIADeepSeekLLM(
                api_key=NVIDIA_API_KEY,
                model=NVIDIA_MODEL,
                temperature=0.1,
                max_tokens=1000
            )
            
            logger.info(f"✅ LLM initialized: {NVIDIA_MODEL}")
            
            # Initialize vector store
            self.vector_store = VectorStore()
            logger.info("✅ Vector store (Chroma) initialized")
            
            self.qa_chain = None
            logger.info("✅ RAG Agent ready!")
            
        except Exception as e:
            logger.error(f"❌ Error initializing RAG Agent: {str(e)}")
            raise
    
    def setup_qa_chain(self, vectorstore, custom_prompt: str = None):
        """
        Setup QA chain with retriever
        
        Args:
            vectorstore: Chroma vectorstore
            custom_prompt: Custom prompt template
        
        Returns:
            RetrievalQA chain
        """
        
        if custom_prompt is None:
            custom_prompt = """You are a helpful assistant analyzing documents. 
Use the following pieces of context to answer the question at the end.
If you don't know the answer based on the provided documents, say "I don't know" or "This information is not in the provided documents."

Context:
{context}

Question: {question}

Answer:"""
        
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=custom_prompt
        )
        
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template}
        )
        
        logger.info("✅ QA chain setup completed")
        return qa_chain
    
    def analyze_documents(self, vectorstore, question: str) -> Dict[str, Any]:
        """
        Analyze documents and answer question
        
        Args:
            vectorstore: Chroma vectorstore
            question: User question
        
        Returns:
            Answer with source documents
        """
        try:
            # Setup chain
            qa_chain = self.setup_qa_chain(vectorstore)
            
            logger.info(f"🔍 Processing question: {question}")
            
            # Get answer from DeepSeek
            result = qa_chain({"query": question})
            
            # Extract sources
            sources = []
            if "source_documents" in result:
                sources = [
                    {
                        "content": doc.page_content[:300],
                        "metadata": doc.metadata
                    }
                    for doc in result["source_documents"]
                ]
            
            logger.info(f"✅ Got answer with {len(sources)} sources")
            
            return {
                "answer": result.get("result", ""),
                "sources": sources,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing documents: {str(e)}")
            return {
                "answer": f"Error: {str(e)}",
                "sources": [],
                "success": False
            }
    
    def get_summary(self, vectorstore, num_chunks: int = 5) -> str:
        """
        Get a summary of uploaded documents
        
        Args:
            vectorstore: Chroma vectorstore
            num_chunks: Number of chunks to summarize
        
        Returns:
            Summary text
        """
        try:
            logger.info("📝 Generating summary...")
            
            # Search for general content
            results = vectorstore.similarity_search(
                "summary overview main points", 
                k=num_chunks
            )
            
            if not results:
                return "No documents found to summarize"
            
            # Combine chunks
            combined_text = "\n\n".join([doc.page_content for doc in results])
            
            # Use DeepSeek to summarize
            summary_prompt = f"""Provide a concise and comprehensive summary of the following document:

{combined_text}

Summary:"""
            
            logger.info("🔄 Calling DeepSeek for summary...")
            response = self.llm._call(summary_prompt)
            
            logger.info("✅ Summary generated")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generating summary: {str(e)}")
            return "Error generating summary"

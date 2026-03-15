"""
Embeddings and vector database management with Chroma (LOCAL - NO API KEY!)
"""

import logging
from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

from src.config import CHROMA_DB_PATH, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

class VectorStore:
    """Manage vector embeddings and storage with Chroma (LOCAL)"""
    
    def __init__(self):
        """Initialize vector store with HuggingFace embeddings"""
        try:
            # Initialize embeddings with HuggingFace (FREE, no API key!)
            self.embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={"device": "cpu"}
            )
            
            logger.info("✅ HuggingFace Embeddings initialized (FREE!)")
            logger.info(f"✅ Chroma DB path: {CHROMA_DB_PATH}")
            
        except Exception as e:
            logger.error(f"❌ Error initializing embeddings: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Document], collection_name: str = "documents"):
        """
        Add documents to Chroma vector store
        
        Args:
            documents: List of Document objects
            collection_name: Collection name in Chroma
        """
        try:
            logger.info(f"Adding {len(documents)} documents to Chroma...")
            
            # Create Chroma vectorstore
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=CHROMA_DB_PATH,
                collection_name=collection_name
            )
            
            logger.info(f"✅ Successfully added documents to Chroma")
            return vectorstore
            
        except Exception as e:
            logger.error(f"❌ Error adding documents: {str(e)}")
            return None
    
    def get_vectorstore(self, collection_name: str = "documents"):
        """Get existing Chroma vectorstore"""
        try:
            vectorstore = Chroma(
                persist_directory=CHROMA_DB_PATH,
                embedding_function=self.embeddings,
                collection_name=collection_name
            )
            logger.info(f"✅ Loaded Chroma vectorstore: {collection_name}")
            return vectorstore
        except Exception as e:
            logger.error(f"❌ Error loading vectorstore: {str(e)}")
            return None
    
    def search(self, query: str, k: int = 5, collection_name: str = "documents") -> List[Document]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of results
            collection_name: Collection name
        
        Returns:
            List of relevant documents
        """
        try:
            vectorstore = self.get_vectorstore(collection_name)
            if not vectorstore:
                return []
            
            results = vectorstore.similarity_search(query, k=k)
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching: {str(e)}")
            return []
    
    def delete_collection(self, collection_name: str = "documents") -> bool:
        """Delete a Chroma collection"""
        try:
            import shutil
            if collection_name == "documents":
                # Delete the entire Chroma directory
                shutil.rmtree(CHROMA_DB_PATH, ignore_errors=True)
                logger.info(f"✅ Deleted Chroma database")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting collection: {str(e)}")
            return False

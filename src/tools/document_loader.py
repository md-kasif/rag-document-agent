"""
Document loading and processing tools
Supports: PDF, DOCX, XLS, Web URLs
"""

import os
import logging
from typing import List
from pathlib import Path

from langchain.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader,
)
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from src.config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process and chunk documents"""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF file"""
        try:
            logger.info(f"Loading PDF: {file_path}")
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from PDF")
            return documents
        except Exception as e:
            logger.error(f"Error loading PDF: {str(e)}")
            return []
    
    def load_docx(self, file_path: str) -> List[Document]:
        """Load DOCX file"""
        try:
            logger.info(f"Loading DOCX: {file_path}")
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            logger.info(f"Loaded DOCX document")
            return documents
        except Exception as e:
            logger.error(f"Error loading DOCX: {str(e)}")
            return []
    
    def load_excel(self, file_path: str) -> List[Document]:
        """Load Excel file"""
        try:
            logger.info(f"Loading Excel: {file_path}")
            loader = UnstructuredExcelLoader(file_path)
            documents = loader.load()
            logger.info(f"Loaded Excel document")
            return documents
        except Exception as e:
            logger.error(f"Error loading Excel: {str(e)}")
            return []
    
    def load_file(self, file_path: str) -> List[Document]:
        """Load any supported file based on extension"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == ".pdf":
            return self.load_pdf(file_path)
        elif file_ext == ".docx":
            return self.load_docx(file_path)
        elif file_ext in [".xlsx", ".xls"]:
            return self.load_excel(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_ext}")
            return []
    
    def load_web_url(self, url: str) -> List[Document]:
        """Load content from a web URL"""
        try:
            logger.info(f"Loading from URL: {url}")
            loader = WebBaseLoader(url)
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} documents from URL")
            return documents
        except Exception as e:
            logger.error(f"Error loading URL: {str(e)}")
            return []
    
    def load_web_urls(self, urls: List[str]) -> List[Document]:
        """Load content from multiple URLs"""
        all_documents = []
        for url in urls:
            documents = self.load_web_url(url)
            all_documents.extend(documents)
        return all_documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        try:
            logger.info(f"Chunking {len(documents)} documents...")
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error chunking documents: {str(e)}")
            return []
    
    def process_files(self, file_paths: List[str]) -> List[Document]:
        """Process multiple files"""
        all_documents = []
        for file_path in file_paths:
            documents = self.load_file(file_path)
            all_documents.extend(documents)
        
        chunks = self.chunk_documents(all_documents)
        return chunks
    
    def process_urls(self, urls: List[str]) -> List[Document]:
        """Process multiple URLs"""
        documents = self.load_web_urls(urls)
        chunks = self.chunk_documents(documents)
        return chunks
    
    def process_mixed(self, files: List[str], urls: List[str]) -> List[Document]:
        """Process both files and URLs"""
        all_documents = []
        
        if files:
            file_chunks = self.process_files(files)
            all_documents.extend(file_chunks)
        
        if urls:
            url_chunks = self.process_urls(urls)
            all_documents.extend(url_chunks)
        
        logger.info(f"Total chunks processed: {len(all_documents)}")
        return all_documents

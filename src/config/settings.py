"""Configuration settings for RAG Document Agent"""
import os
from dotenv import load_dotenv

load_dotenv()

# ===== NVIDIA Build Configuration (DeepSeek) =====
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# CORRECT MODEL NAME (from NVIDIA Build screenshot)
NVIDIA_MODEL = "deepseek-ai/deepseek-v3.2"

# ===== Chroma Vector DB (Local - No API Key!) =====
CHROMA_DB_PATH = "chroma_db"

# ===== HuggingFace Embeddings (Free!) =====
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ===== File Processing Configuration =====
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 50))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

# ===== Logging Configuration =====
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ===== Directory Configuration =====
UPLOAD_DIR = "uploads"
DATA_DIR = "data"
LOGS_DIR = "logs"

# Create directories if they don't exist
for directory in [UPLOAD_DIR, DATA_DIR, LOGS_DIR, CHROMA_DB_PATH]:
    os.makedirs(directory, exist_ok=True)

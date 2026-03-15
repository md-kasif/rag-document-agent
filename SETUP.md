# Setup & Installation Guide

## 📋 Prerequisites

- Python 3.11+
- pip (Python package manager)
- Git
- AWS account (for EC2) or local machine
- NVIDIA Build API key (free from https://build.nvidia.com/)
- ~500MB free disk space

---

## 🚀 Installation Steps

### **1. Clone Repository**

```bash
git clone https://github.com/yourusername/rag-document-agent.git
cd rag-document-agent

2. Create Virtual Environment
bash

Copy code
# Create
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows - PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Windows - CMD)
venv\Scripts\activate.bat

# Verify
which python  # Should show venv path

3. Install Dependencies
bash

Copy code
# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt

# Verify
pip list | grep langchain

4. Configure Environment
bash

Copy code
# Copy example
cp .env.example .env

# Edit .env
nano .env

# Add your NVIDIA API key:
# NVIDIA_API_KEY=nvapi_your_actual_key_here
# (Save: Ctrl+O, Enter, Ctrl+X)

# Verify
cat .env | grep NVIDIA_API_KEY

5. Create Directories (if not present)
bash

Copy code
mkdir -p uploads chroma_db logs

6. Test Installation
bash

Copy code
python << 'EOF'
import sys
sys.path.insert(0, '.')

from src.agents.rag_agent import RAGAgent
from src.tools.document_loader import DocumentProcessor
from src.tools.embeddings import VectorStore

print("✅ All imports successful!")
print("✅ Installation complete!")

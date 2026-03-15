"""
Streamlit Frontend for RAG Document Agent
Developed by Md Kasif
Powered by DeepSeek v3.2 + Chroma + HuggingFace
"""

import streamlit as st
import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.agents.rag_agent import RAGAgent
from src.tools.document_loader import DocumentProcessor
from src.tools.embeddings import VectorStore
from src.config import UPLOAD_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="RAG Document Agent",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .stButton > button {
        width: 100%;
        height: 40px;
        font-size: 16px;
        font-weight: bold;
    }
    .developer-note {
        text-align: center;
        color: #888;
        font-size: 12px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# TITLE & INTRO
# ============================================================================

col1, col2 = st.columns([3, 1])
with col1:
    st.title("📄 RAG Document Agent")
    st.write("**Upload documents or provide URLs, then ask questions!**")
with col2:
    st.markdown("🚀 Powered by **DeepSeek v3.2**")

st.divider()

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header("⚙️ Configuration")
    
    mode = st.radio(
        "Select Mode:",
        ["📤 Upload Documents", "❓ Ask Questions", "📊 Document Summary"],
        key="mode_selector"
    )
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Clear", use_container_width=True):
            vector_store = VectorStore()
            if vector_store.delete_collection():
                st.success("✅ Cleared!")
                st.session_state.documents_loaded = False
                st.rerun()
            else:
                st.error("Error clearing")
    
    with col2:
        if st.button("ℹ️ Info", use_container_width=True):
            st.info("RAG Document Agent\nDeepSeek + Chroma + HuggingFace")
    
    st.divider()
    st.caption("📝 Made with LangChain + Streamlit")
    
    # Developer credit
    st.divider()
    st.markdown("""
    <div class="developer-note">
    <p><strong>Developed by</strong></p>
    <p style="color: #1f77b4; font-weight: bold; font-size: 14px;">Md Kasif</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'rag_agent' not in st.session_state:
    try:
        st.session_state.rag_agent = RAGAgent()
    except Exception as e:
        st.error(f"❌ Error initializing RAG Agent: {str(e)}")

# ============================================================================
# MODE 1: UPLOAD DOCUMENTS
# ============================================================================

if mode == "📤 Upload Documents":
    st.header("Upload Documents & URLs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Upload Files")
        st.caption("PDF, DOCX, XLS files")
        uploaded_files = st.file_uploader(
            "Choose files",
            type=["pdf", "docx", "xlsx", "xls"],
            accept_multiple_files=True,
            key="file_uploader"
        )
    
    with col2:
        st.subheader("🌐 Add URLs")
        st.caption("One URL per line")
        url_input = st.text_area(
            "Enter URLs:",
            placeholder="https://example.com/page1\nhttps://example.com/page2",
            height=150,
            key="url_input"
        )
    
    st.divider()
    
    if st.button("🚀 Process Documents", type="primary", use_container_width=True):
        
        files_to_process = []
        urls_to_process = []
        
        # Handle uploaded files
        if uploaded_files:
            with st.status("📥 Saving uploaded files..."):
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    files_to_process.append(file_path)
                    st.write(f"✅ Saved: {uploaded_file.name}")
        
        # Handle URLs
        if url_input:
            urls_to_process = [url.strip() for url in url_input.split("\n") if url.strip()]
        
        # Process documents
        if files_to_process or urls_to_process:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Load documents
                status_text.text("📖 Loading documents...")
                progress_bar.progress(25)
                
                processor = DocumentProcessor()
                all_documents = processor.process_mixed(files_to_process, urls_to_process)
                
                if not all_documents:
                    st.error("❌ No documents loaded. Check file formats and URLs.")
                else:
                    # Step 2: Create embeddings
                    status_text.text("🧠 Creating embeddings and storing in Chroma...")
                    progress_bar.progress(50)
                    
                    vector_store = VectorStore()
                    vectorstore = vector_store.add_documents(all_documents)
                    
                    if vectorstore:
                        progress_bar.progress(100)
                        status_text.text("✅ Processing complete!")
                        
                        # Save to session state
                        st.session_state.vectorstore = vectorstore
                        st.session_state.documents_loaded = True
                        
                        st.success(f"✅ Successfully processed {len(all_documents)} chunks!")
                        st.info(f"📊 Total files: {len(files_to_process)} | 🌐 Total URLs: {len(urls_to_process)}")
                    else:
                        st.error("❌ Error creating embeddings")
                        
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Error processing documents: {str(e)}")
        else:
            st.warning("⚠️ Please upload files or provide URLs")

# ============================================================================
# MODE 2: ASK QUESTIONS
# ============================================================================

elif mode == "❓ Ask Questions":
    st.header("Ask Questions About Your Documents")
    
    if not st.session_state.documents_loaded:
        st.warning("⚠️ Please upload documents first in '📤 Upload Documents' tab!")
    else:
        st.success("✅ Documents loaded and ready!")
        
        # Question input
        question = st.text_input(
            "Ask a question:",
            placeholder="What is this document about?",
            key="question_input"
        )
        
        if st.button("🔍 Search & Answer", type="primary", use_container_width=True):
            if not question:
                st.warning("⚠️ Please enter a question")
            else:
                with st.spinner("🤔 Thinking..."):
                    try:
                        result = st.session_state.rag_agent.analyze_documents(
                            st.session_state.vectorstore,
                            question
                        )
                        
                        if result['success']:
                            # Display answer
                            st.subheader("💡 Answer")
                            st.markdown(result['answer'])
                            
                            # Display sources
                            if result['sources']:
                                st.divider()
                                st.subheader("📚 Source Documents")
                                for i, source in enumerate(result['sources'], 1):
                                    with st.expander(f"Source {i}"):
                                        st.write(source['content'])
                                        st.caption(str(source['metadata']))
                        else:
                            st.error(f"❌ Error: {result['answer']}")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        logger.error(f"Error analyzing documents: {str(e)}")

# ============================================================================
# MODE 3: DOCUMENT SUMMARY
# ============================================================================

elif mode == "📊 Document Summary":
    st.header("Document Summary")
    
    if not st.session_state.documents_loaded:
        st.warning("⚠️ Please upload documents first!")
    else:
        st.success("✅ Documents loaded!")
        
        if st.button("📋 Generate Summary", type="primary", use_container_width=True):
            with st.spinner("✍️ Generating summary..."):
                try:
                    summary = st.session_state.rag_agent.get_summary(
                        st.session_state.vectorstore,
                        num_chunks=5
                    )
                    st.markdown(summary)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"Error generating summary: {str(e)}")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🤖 Powered by DeepSeek v3.2")
with col2:
    st.caption("🗂️ Chroma Vector DB")
with col3:
    st.caption("⚡ Built with Streamlit")

st.divider()

# Developer credit in footer
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
with footer_col2:
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px; margin-top: 10px;">
    <p><strong>Developed by</strong> <span style="color: #1f77b4; font-weight: bold;">Md Kasif</span></p>
    <p style="font-size: 10px; color: #999;">RAG Document Agent | DeepSeek + Chroma</p>
    </div>
    """, unsafe_allow_html=True)

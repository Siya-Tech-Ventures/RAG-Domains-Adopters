import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import os
from rag_engine import FinanceRAG
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Function to get OpenAI API key
def get_openai_api_key():
    """Get OpenAI API key from environment variable or user input"""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    return None

# Function to check if API key is valid (basic check)
def is_api_key_valid(api_key):
    """Basic validation of API key format"""
    if not api_key:
        return False
    # Check if key starts with "sk-" and has reasonable length
    return api_key.startswith("sk-") and len(api_key) > 20

# Page configuration
st.set_page_config(
    page_title="Finance RAG System",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = None
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False

# Sidebar for configuration
with st.sidebar:
    st.title("💰 Finance RAG")
    
    # Get API key from environment or user
    api_key = get_openai_api_key()
    if not api_key:
        api_key = st.text_input(
            "OpenAI API Key (Required)", 
            type="password",
            help="Enter your OpenAI API key. The key will not be stored permanently."
        )
    
    # Validate API key
    if api_key:
        if is_api_key_valid(api_key):
            st.session_state.api_key_valid = True
            os.environ["OPENAI_API_KEY"] = api_key
            st.success("API key is valid! ✅")
        else:
            st.session_state.api_key_valid = False
            st.error("Invalid API key format. Please check your key.")
    
    # Data directory input
    data_dir = st.text_input("Data Directory", "sample_data")
    processed_docs_dir = os.path.join(data_dir, "processed_docs")
    
    # Create processed_docs directory if it doesn't exist
    if not os.path.exists(processed_docs_dir):
        os.makedirs(processed_docs_dir)
    
    # Initialize systems button
    if st.button("Initialize Systems"):
        if not st.session_state.api_key_valid:
            st.error("Please provide a valid OpenAI API key first!")
        else:
            try:
                st.session_state.rag_system = FinanceRAG(processed_docs_dir)
                st.session_state.rag_system.load_documentation()
                st.success("Systems initialized successfully!")
            except Exception as e:
                st.error(f"Error initializing systems: {str(e)}")

# Main content
st.title("Finance RAG System")

# Check if API key is valid before showing main content
if not st.session_state.api_key_valid:
    st.warning("Please enter a valid OpenAI API key in the sidebar to continue.")
else:
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Market Analysis", "Documentation Query", "Upload Files"])
    
    # Market Analysis Tab
    with tab1:
        st.header("Market Analysis")
        if st.session_state.rag_system:
            query = st.text_input("Enter your market analysis query:")
            if query:
                try:
                    response = st.session_state.rag_system.query_documentation(query, "market_analysis")
                    st.write(response)
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
        else:
            st.warning("Please initialize the system first!")
    
    # Documentation Query Tab
    with tab2:
        st.header("Documentation Query")
        
        if st.session_state.rag_system:
            # Category selection
            categories = st.session_state.rag_system.get_available_categories()
            category = st.selectbox("Select Category", categories)
            
            # Query input
            query = st.text_input("Enter your query:")
            if query:
                try:
                    response = st.session_state.rag_system.query_documentation(query, category)
                    st.write(response)
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
        else:
            st.warning("Please initialize the system first!")
    
    # Upload Files Tab
    with tab3:
        st.header("Upload Files")
        
        # File category selection
        category = st.selectbox(
            "Select Document Category",
            ["market_analysis", "financial_reports", "investment_strategies", "risk_management"]
        )
        
        # Multiple file uploader
        uploaded_files = st.file_uploader(
            "Choose files to upload", 
            type=['txt', 'pdf', 'doc', 'docx'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.session_state.rag_system:
                # Create a progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                processed_files = []
                failed_files = []
                
                for idx, uploaded_file in enumerate(uploaded_files):
                    try:
                        # Update progress
                        progress = (idx + 1) / len(uploaded_files)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing file {idx + 1} of {len(uploaded_files)}: {uploaded_file.name}")
                        
                        # Create a temporary file to store the uploaded content
                        temp_file_path = os.path.join(data_dir, uploaded_file.name)
                        with open(temp_file_path, "wb") as f:
                            f.write(uploaded_file.getvalue())
                        
                        # Process the uploaded file
                        processed_path = st.session_state.rag_system._process_document(temp_file_path, category)
                        processed_files.append(uploaded_file.name)
                        
                        # Remove temporary file
                        os.remove(temp_file_path)
                        
                    except Exception as e:
                        failed_files.append((uploaded_file.name, str(e)))
                
                # Clear progress bar and status text
                progress_bar.empty()
                status_text.empty()
                
                # Reload documentation in RAG system after processing all files
                if st.session_state.rag_system:
                    st.session_state.rag_system.load_documentation()
                
                # Show results
                if processed_files:
                    st.success(f"Successfully processed {len(processed_files)} files:")
                    for file in processed_files:
                        st.write(f"✅ {file}")
                
                if failed_files:
                    st.error(f"Failed to process {len(failed_files)} files:")
                    for file, error in failed_files:
                        st.write(f"❌ {file}: {error}")
                
            else:
                st.warning("Please initialize the systems first using the button in the sidebar.")

# Footer
st.markdown("---")
st.markdown("Finance RAG System - Powered by OpenAI and LangChain")

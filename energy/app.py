import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import os
from rag_engine import EnergyMaintenanceRAG
from ingestion import MaintenanceDataIngestion
import json
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
    page_title="Energy Maintenance RAG System",
    page_icon="⚡",
    layout="wide"
)

# Initialize session state
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = None
if 'ingestion_system' not in st.session_state:
    st.session_state.ingestion_system = None
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False

# Sidebar for configuration
with st.sidebar:
    st.title("⚡ Energy RAG")
    
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
                st.session_state.ingestion_system = MaintenanceDataIngestion(data_dir)
                st.session_state.rag_system = EnergyMaintenanceRAG(processed_docs_dir)
                
                # Process sample data with the correct data directory
                st.session_state.ingestion_system.process_sample_data(
                    sample_data_dir=os.path.join(os.path.dirname(__file__), "sample_data")
                )
                
                # Load processed documentation
                st.session_state.rag_system.load_documentation()
                st.success("Systems initialized successfully!")
            except Exception as e:
                st.error(f"Error initializing systems: {str(e)}")

# Main content
st.title("Energy Maintenance RAG System")

# Check if API key is valid before showing main content
if not st.session_state.api_key_valid:
    st.warning("Please provide a valid OpenAI API key in the sidebar to use the system.")
    st.stop()

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Equipment Health", 
    "Documentation Query",
    "Maintenance Schedule", 
    "Data Management",
    "Upload Files"
])

# Equipment Health Tab
with tab1:
    st.header("Equipment Health Analysis")
    
    equipment_id = st.text_input("Equipment ID", value="SF-TRB-2024-103", key="health_equipment_id")
    st.markdown("""
    **Sample Queries:**
    - What is the maintenance history of SF-TRB-2024-103?
    - Are there any recurring issues with SF-TRB-2024-103?
    - When was the last maintenance performed on SF-TRB-2024-103?
    """)
    if st.button("Analyze Health", key="analyze_health"):
        if st.session_state.rag_system:
            query = f"What is the current health status and maintenance history of equipment {equipment_id}?"
            result = st.session_state.rag_system.query_documentation(
                query, 
                category="equipment_health"
            )
            st.write("Analysis Results:")
            st.write(result)
        else:
            st.warning("Please initialize the system first!")

# Documentation Query Tab
with tab2:
    st.header("Documentation Query")
    
    # Category selection
    if st.session_state.rag_system:
        categories = ["all"] + st.session_state.rag_system.get_available_categories()
        selected_category = st.selectbox(
            "Select Documentation Category",
            categories,
            key="doc_category"
        )
    
    query = st.text_area("Enter your query", value="What are the common maintenance procedures for wind turbines?")
    st.markdown("""
    **Sample Queries:**
    - What are the safety protocols for high-voltage equipment maintenance?
    - How often should we perform preventive maintenance on solar panels?
    - What are the troubleshooting steps for generator overheating?
    """)
    if st.button("Search", key="search_docs"):
        if st.session_state.rag_system:
            category = None if selected_category == "all" else selected_category
            result = st.session_state.rag_system.query_documentation(query, category=category)
            st.write("Search Results:")
            st.write(result)
        else:
            st.warning("Please initialize the system first!")

# Maintenance Schedule Tab
with tab3:
    st.header("Maintenance Schedule")
    
    schedule_query = st.text_area(
        "Enter maintenance schedule query",
        value="List all scheduled maintenance tasks for wind turbines in the next month",
        key="schedule_query"
    )
    st.markdown("""
    **Sample Queries:**
    - What maintenance tasks are overdue?
    - Show me the preventive maintenance schedule for Q4 2023
    - Which equipment requires immediate maintenance attention?
    """)
    if st.button("Get Schedule", key="get_schedule"):
        if st.session_state.rag_system:
            result = st.session_state.rag_system.query_documentation(
                schedule_query,
                category="maintenance_schedule"
            )
            st.write("Maintenance Schedule:")
            st.write(result)
        else:
            st.warning("Please initialize the system first!")

# Data Management Tab
with tab4:
    st.header("Data Management")
    
    st.subheader("Available Documentation")
    if st.session_state.rag_system:
        categories = st.session_state.rag_system.get_available_categories()
        for category in categories:
            st.write(f"✓ {category.replace('_', ' ').title()}")
    
    if st.button("Refresh Data", key="refresh_data"):
        if st.session_state.ingestion_system and st.session_state.rag_system:
            try:
                st.session_state.ingestion_system.process_sample_data(
                    sample_data_dir=os.path.join(os.path.dirname(__file__), "sample_data")
                )
                st.session_state.rag_system.load_documentation()
                st.success("Data refreshed successfully!")
            except Exception as e:
                st.error(f"Error refreshing data: {str(e)}")
        else:
            st.warning("Please initialize the system first!")

# Upload Files Tab
with tab5:
    st.header("Upload Files")
    
    # File category selection
    category = st.selectbox(
        "Select Document Category",
        ["equipment_health", "maintenance_schedule", "technical_documentation", "data_ingestion"]
    )
    
    # Multiple file uploader
    uploaded_files = st.file_uploader(
        "Choose files to upload", 
        type=['txt', 'pdf', 'doc', 'docx'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.session_state.ingestion_system:
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
                    processed_path = st.session_state.ingestion_system._process_document(temp_file_path, category)
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
st.markdown("Energy Maintenance RAG System - Powered by OpenAI and LangChain")

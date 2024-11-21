import streamlit as st
import os
import json
from ingestion import DataIngestion
from rag_engine import RealEstateRAG

# Initialize RAG and ingestion components
@st.cache_resource
def initialize_components():
    rag = RealEstateRAG()
    ingestion = DataIngestion()
    
    # Ingest existing data from data folder
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if os.path.exists(data_dir):
        with st.spinner("Loading existing real estate data..."):
            try:
                documents = ingestion.ingest_directory(data_dir)
                if documents:
                    rag.ingest_documents(documents)
                    st.success(f"Successfully loaded existing data from {data_dir}")
            except Exception as e:
                st.error(f"Error loading existing data: {str(e)}")
    
    return rag, ingestion

def main():
    st.title("Real Estate RAG Assistant ")
    
    # Initialize components
    rag, ingestion = initialize_components()
    
    # Sidebar for data ingestion
    st.sidebar.title("Document Ingestion")
    
    # Add tabs for different types of documents
    doc_type = st.sidebar.radio(
        "Document Type",
        ["Property Listings", "Legal Documents"],
        help="Choose the type of document you want to process"
    )
    
    if doc_type == "Property Listings":
        # File upload
        uploaded_files = st.sidebar.file_uploader(
            "Upload Real Estate Documents",
            accept_multiple_files=True,
            type=['pdf', 'txt', 'md', 'csv']
        )
        
        # URL input
        urls = st.sidebar.text_area(
            "Enter listing URLs (one per line)",
            height=100
        )
        
        # Manual listing input
        st.sidebar.subheader("Add Listing Manually")
        with st.sidebar.form("listing_form"):
            address = st.text_input("Address")
            price = st.number_input("Price", min_value=0, value=0)
            bedrooms = st.number_input("Bedrooms", min_value=0, value=0)
            bathrooms = st.number_input("Bathrooms", min_value=0.0, value=0.0)
            sqft = st.number_input("Square Footage", min_value=0, value=0)
            property_type = st.selectbox("Property Type", 
                ["Single Family", "Condo", "Townhouse", "Multi-Family", "Land"])
            year_built = st.number_input("Year Built", min_value=1800, max_value=2024, value=2000)
            description = st.text_area("Description")
            features = st.text_area("Features (comma-separated)")
            
            submitted = st.form_submit_button("Add Listing")
        
    else:  # Legal Documents
        # File upload for legal documents
        legal_files = st.sidebar.file_uploader(
            "Upload Legal Documents",
            accept_multiple_files=True,
            type=['pdf', 'txt'],
            help="Upload rental agreements, lease contracts, or other legal documents"
        )
        
        if legal_files:
            for file in legal_files:
                with st.spinner(f"Processing legal document: {file.name}..."):
                    # Save temporarily and process
                    temp_path = os.path.join("data", file.name)
                    with open(temp_path, "wb") as f:
                        f.write(file.getvalue())
                    try:
                        # Process the legal document
                        document_sections = ingestion.processor.process_legal_document(temp_path)
                        # Ingest the full text
                        rag.ingest_documents([document_sections["full_text"]])
                        st.sidebar.success(f"Processed {file.name}")
                    except Exception as e:
                        st.sidebar.error(f"Error processing {file.name}: {str(e)}")

    # Process uploaded files (for property listings)
    if doc_type == "Property Listings" and uploaded_files:
        for file in uploaded_files:
            with st.spinner(f"Processing {file.name}..."):
                # Save temporarily and process
                temp_path = f"temp_{file.name}"
                with open(temp_path, "wb") as f:
                    f.write(file.getvalue())
                try:
                    content = ingestion.ingest_file(temp_path)
                    rag.ingest_documents([content])
                    st.sidebar.success(f"Processed {file.name}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    
    # Process URLs
    if doc_type == "Property Listings" and urls:
        url_list = [url.strip() for url in urls.split('\n') if url.strip()]
        if url_list:
            with st.spinner("Processing URLs..."):
                contents = ingestion.ingest_urls(url_list)
                rag.ingest_documents([c for c in contents if c])
                st.sidebar.success(f"Processed {len(url_list)} URLs")
    
    # Process manual listing
    if doc_type == "Property Listings" and submitted and address:  # Only process if address is provided
        listing_data = {
            "address": address,
            "price": price,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "sqft": sqft,
            "property_type": property_type,
            "year_built": year_built,
            "description": description,
            "features": features
        }
        content = ingestion.processor.process_listing_data(listing_data)
        rag.ingest_documents([content])
        st.sidebar.success("Added listing successfully!")
    
    # Main interface
    if doc_type == "Property Listings":
        st.subheader("Ask Questions About Real Estate")
        chat_placeholder = "Ask about properties, market trends, or specific listings..."
    else:
        st.subheader("Legal Document Analysis")
        # Add analysis options
        analysis_type = st.radio(
            "Choose Analysis Type",
            ["Chat with Documents", "Full Document Analysis"],
            help="Choose how you want to analyze the legal documents"
        )
        
        if analysis_type == "Chat with Documents":
            chat_placeholder = "Ask questions about the legal documents (e.g., 'What are the key terms in the rental agreement?')"
        else:
            if st.button("Analyze Documents"):
                with st.spinner("Analyzing legal documents..."):
                    # Perform comprehensive analysis
                    analysis = rag.analyze_legal_document("")  # Empty string to analyze all ingested documents
                    
                    # Display analysis results in an organized way
                    for question, answer in analysis.items():
                        with st.expander(question):
                            st.write(answer)
            chat_placeholder = "Ask for specific details about the analysis..."

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input(chat_placeholder):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = rag.query(prompt)
                answer = response["answer"]
                sources = response["sources"]
                
                # Display answer
                st.markdown(answer)
                
                # Display sources if available
                if sources:
                    with st.expander("View Sources"):
                        for i, source in enumerate(sources, 1):
                            st.markdown(f"**Source {i}:**\n{source}")
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()

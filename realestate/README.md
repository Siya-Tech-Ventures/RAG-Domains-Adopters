# Real Estate RAG Application

This application demonstrates the power of Retrieval Augmented Generation (RAG) in the real estate domain. It helps users query and analyze real estate documents, listings, market data, and legal documents using natural language processing.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://stv-realestate-rag.streamlit.app/)

![Real Estate RAG Demo](realestate-rag.webp)

## Features

- Document ingestion for real estate listings, market reports, and property descriptions
- Legal document analysis for rental agreements and property contracts
- Natural language querying for property information
- Market analysis and trend identification
- Property comparison and recommendation
- Automated property valuation insights
- Contract loophole detection and legal clause analysis

## Setup

### Option 1: Using Conda (Recommended)

1. Create a conda environment:
```bash
conda env create -f environment.yml
conda activate real-estate-rag
```

### Option 2: Using Python venv

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Common Setup Steps

1. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

2. Run the application:
```bash
streamlit run app.py
```

## Project Structure

- `app.py`: Main Streamlit application
- `ingestion.py`: Document processing and vectorization
- `rag_engine.py`: RAG implementation and query processing
- `utils.py`: Utility functions
- `data/`: Directory for storing real estate documents and embeddings
- `components/`: Streamlit UI components

## Usage

### Property Listings
1. Select "Property Listings" in the sidebar
2. Upload real estate documents (PDFs, text files) through the web interface
3. Ask questions about properties, market trends, or specific listings
4. Get AI-powered insights and recommendations based on the processed documents

### Legal Document Analysis
1. Select "Legal Documents" in the sidebar
2. Upload legal documents (rental agreements, lease contracts, etc.)
3. Choose between:
   - Chat with Documents: Ask specific questions about the legal documents
   - Full Document Analysis: Get comprehensive analysis of potential issues

## Example Queries

### Property Queries
- "What are the average property prices in downtown area?"
- "Compare the features of properties listed in the last month"
- "What are the key market trends in residential properties?"
- "Find properties with similar characteristics to [address]"

### Legal Document Queries
- "What are the main terms and conditions in this rental agreement?"
- "Are there any potential loopholes in the contract?"
- "What are the tenant's rights and obligations?"
- "Explain the termination conditions in the lease"
- "Are there any missing important clauses in this agreement?"

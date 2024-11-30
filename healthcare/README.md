# Healthcare Regulatory Compliance Assistant

A RAG-based chatbot designed to assist with healthcare regulatory compliance queries. The system uses Google's Gemini Pro model combined with OpenAI embeddings to provide accurate information from regulatory documents.

## Live Demo
🔗 [Healthcare RAG System](https://stv-healthcare-rag.streamlit.app/)

![Healthcare RAG System](healthcare-rag.webp)

## Features

- Powered by Google's Gemini Pro LLM for response generation
- OpenAI embeddings for accurate document retrieval
- RAG (Retrieval Augmented Generation) for accurate responses
- Interactive Streamlit interface with suggested questions
- Source context display for transparency
- Persistent vector storage using Chroma
- Support for both PDF and text documents
- Automatic question generation from document content

## Setup

### Option 1: Using Conda (Recommended)

1. Create and activate a new Conda environment:
```bash
# Create environment from yml file
conda env create -f environment.yml

# Activate the environment
conda activate healthcare-rag

# Verify installation
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
```

2. Install additional dependencies:
```bash
pip install -r requirements.txt
```

### Option 2: Using pip

1. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Configuration

1. Create a `.env` file with your API keys:
```
GOOGLE_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
```

2. Add regulatory documents:
   - Place PDF or text files in the `data` directory
   - Supported formats: `.pdf`, `.txt`
   - Documents will be automatically processed and indexed

3. Run the application:
```bash
streamlit run app.py
```

## Implementation Details

The system implements a RAG architecture with the following components:

1. **Document Processing:**
   - Support for PDF and text documents
   - Recursive text splitting for optimal chunk size
   - OpenAI embeddings for high-quality document representation
   - Chroma vector store for efficient retrieval

2. **Query Processing:**
   - Semantic similarity search with configurable k-nearest neighbors
   - Context-aware prompt construction
   - Gemini Pro for response generation
   - Source attribution in responses

3. **User Interface:**
   - Chat-based interaction
   - AI-generated suggested questions
   - Source context visualization
   - Document upload functionality
   - Error handling and API key validation

## Usage

1. Start the application using `streamlit run app.py`
2. Upload your regulatory documents (PDF or text files)
3. Use the suggested questions or type your own queries
4. View AI responses with source context
5. Explore the "View Source Context" section for reference material

## Project Structure

- `app.py`: Main application with RAG implementation
- `data/`: Directory for regulatory documents (PDF/TXT)
- `requirements.txt`: Python dependencies
- `environment.yml`: Conda environment specification
- `.env`: Environment variables (API keys)
- `chroma_db/`: Persistent vector store (auto-generated)

## Environment Variables

Required environment variables in `.env`:
- `GOOGLE_API_KEY`: Gemini Pro API key for text generation
- `OPENAI_API_KEY`: OpenAI API key for embeddings

## Troubleshooting

Common issues and solutions:

1. **CUDA/GPU Issues**:
   - If you encounter CUDA errors, ensure your NVIDIA drivers are up to date
   - For CPU-only installation, use: `conda install pytorch cpuonly -c pytorch`

2. **Environment Setup**:
   - If Conda environment creation fails, try updating Conda: `conda update -n base conda`
   - For M1/M2 Macs, use: `CONDA_SUBDIR=osx-arm64 conda env create -f environment.yml`

3. **API Keys**:
   - Ensure both API keys are properly set in the `.env` file
   - Verify API key permissions and quotas in respective dashboards

## Notes

- The system uses OpenAI embeddings for better retrieval accuracy
- Documents are automatically processed when added to the data directory
- Suggested questions are generated based on document content
- The vector store is persistent and will retain indexed documents
- For optimal performance, consider using a GPU-enabled environment
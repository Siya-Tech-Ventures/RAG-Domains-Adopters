# Energy Sector RAG System for Predictive Maintenance

This system implements a Retrieval-Augmented Generation (RAG) approach for predictive maintenance in the energy sector. It helps analyze equipment documentation, maintenance records, and performance data to predict and prevent potential issues before they occur.

## Setup

1. Create and activate the conda environment:
```bash
conda env create -f environment.yml
conda activate energy-rag
```

2. Set up your OpenAI API key in one of two ways:
   - Create a `.env` file from the template and add your API key:
     ```bash
     cp .env.template .env
     # Edit .env and add your OpenAI API key
     ```
   - Or provide your API key directly in the Streamlit interface when prompted

3. Run the Streamlit app:
```bash
streamlit run app.py
```

## Features

- Document processing for technical manuals and maintenance records
- Performance data analysis and pattern recognition
- Equipment-specific maintenance recommendations
- Historical maintenance data integration
- Real-time monitoring and alerts
- Customized query interface for maintenance staff

## Components

1. Data Ingestion
   - Process technical documentation
   - Import maintenance records
   - Parse equipment performance data

2. RAG Engine
   - Specialized embeddings for technical terminology
   - Context-aware retrieval system
   - Custom prompt templates for maintenance queries

3. Analysis Engine
   - Pattern recognition for equipment behavior
   - Anomaly detection
   - Maintenance schedule optimization

## Usage

The system can be used to:
- Query equipment maintenance procedures
- Analyze historical performance patterns
- Predict potential equipment failures
- Generate maintenance schedules
- Access relevant technical documentation
- Get real-time equipment status updates

## Security Note

The OpenAI API key is handled securely:
- If provided via environment variable, it's loaded automatically
- If provided via the UI, it's only stored in memory during the session
- The key is validated before use
- The key is never logged or stored permanently

# Financial Analysis RAG System

A sophisticated Retrieval-Augmented Generation (RAG) system designed for financial document analysis, market insights, and investment research. This system leverages OpenAI's capabilities to process financial documents, analyze market data, and generate actionable investment insights.

## Features

### Document Analysis
- Financial statement analysis (Balance sheets, Income statements, Cash flow statements)
- SEC filing processing and summarization
- Earnings call transcript analysis
- News and market report interpretation
- Regulatory compliance document processing

### Market Analysis
- Real-time market data integration
- Technical indicator analysis
- Market sentiment analysis
- Trend identification and prediction
- Sector and industry analysis

### Investment Insights
- Company fundamental analysis
- Risk assessment and portfolio recommendations
- Peer comparison and benchmarking
- Investment strategy evaluation
- ESG factor analysis

## Technical Architecture

1. Data Ingestion Layer
   - Document processing pipeline for various financial formats
   - Real-time market data integration
   - News and social media feed processing

2. RAG Engine
   - Custom embeddings for financial terminology
   - Context-aware retrieval system
   - Financial domain-specific prompt templates

3. Analysis Engine
   - Quantitative analysis tools
   - Pattern recognition algorithms
   - Risk assessment models

## Setup

### Option 1: Using Conda (Recommended)

1. Create and activate the conda environment:
```bash
conda env create -f environment.yml
conda activate finance-rag
```

### Option 2: Using Python venv

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Configuration

1. Create a `.env` file with your API keys:
```bash
cp .env.template .env
```

2. Add the following to your `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here  # For market data
NEWS_API_KEY=your_news_api_key_here  # For news feed
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage Examples

1. Financial Document Analysis:
   - Upload financial statements for automated analysis
   - Query specific financial metrics and ratios
   - Generate summary reports and insights

2. Market Analysis:
   - Real-time market data visualization
   - Technical analysis with custom indicators
   - Market sentiment tracking

3. Investment Research:
   - Company fundamental analysis
   - Peer comparison and benchmarking
   - Portfolio optimization suggestions

## Data Sources

The system integrates with various financial data sources:
- Alpha Vantage for market data
- News API for current events
- SEC EDGAR for company filings
- Financial statements and reports
- Market research documents

## Security Considerations

- All API keys are stored securely in `.env`
- Data encryption for sensitive financial information
- Rate limiting for API calls
- Access control for sensitive financial data

## Dependencies

Key dependencies include:
- OpenAI for RAG capabilities
- Streamlit for web interface
- Pandas for data manipulation
- Plotly for interactive visualizations
- yfinance for market data
- PyPDF2 for PDF processing

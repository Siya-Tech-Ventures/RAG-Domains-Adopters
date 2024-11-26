# RAG-Domains-Adopters

This repository showcases practical implementations of Retrieval-Augmented Generation (RAG) across different business domains. Each subdirectory contains a complete, domain-specific RAG application that demonstrates how to effectively leverage RAG for real-world use cases.

## Project Structure

The repository is organized into domain-specific directories:

### 🏭 Energy Domain (`/energy`)
A RAG-powered application focused on predictive maintenance in the energy sector:
- Equipment maintenance prediction and monitoring
- Technical documentation analysis
- Performance data analysis and pattern recognition
- Real-time monitoring and alerts
- Customized query interface for maintenance staff

### 💰 Finance Domain (`/finance`)
A RAG implementation for financial analysis and compliance:
- Financial document processing
- Market data analysis
- Investment insights generation

### 🏥 Healthcare Domain (`/healthcare`)
A regulatory compliance assistant powered by Google's Gemini Pro:
- Healthcare regulatory document analysis
- Interactive compliance query system
- Source context display for transparency
- Automatic question generation from documents
- Support for PDF and text documents

### 🏘️ Real Estate Domain (`/realestate`)
A comprehensive real estate analysis system:
- Property listing and market data analysis
- Legal document processing for agreements
- Market trend identification
- Automated property valuation insights
- Contract analysis and legal clause detection

### 🏏 Sports Domain (`/sports`)
A cricket match analysis system powered by Google's Gemini Pro:
- Comprehensive match analysis and statistics
- Partnership and player performance tracking
- Phase-wise analysis (powerplay, middle overs, death overs)
- Risk analysis and scoring patterns
- Interactive match visualization

## Features

- **Domain-Specific RAG Implementations**: Each domain showcases tailored RAG solutions
- **Multiple LLM Support**: Integration with both OpenAI and Google's Gemini Pro
- **Interactive Web Interfaces**: Built with Streamlit for user-friendly interaction
- **Document Processing**: Efficient ingestion and processing of domain-specific documents
- **Intelligent Querying**: Natural language querying with context-aware responses
- **Visualization**: Interactive data visualization and insights

## Prerequisites

- Python 3.8+
- OpenAI API key (for OpenAI-based implementations)
- Google API key (for Gemini Pro implementations)
- Required Python packages (specified in each domain's `requirements.txt` or `environment.yml`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/RAG-Domains-Adopters.git
   cd RAG-Domains-Adopters
   ```

2. Choose your preferred setup method for specific domain:

   ### Using Conda (Recommended)
   ```bash
   cd <domain-directory>
   conda env create -f environment.yml
   conda activate <domain>-rag
   ```

   ### Using Python venv
   ```bash
   cd <domain-directory>
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.template` to `.env` in the domain directory
   - Add required API keys to `.env`

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

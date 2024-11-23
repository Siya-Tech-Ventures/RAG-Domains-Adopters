# RAG-Domains-Adopters

This repository showcases practical implementations of Retrieval-Augmented Generation (RAG) across different business domains. Each subdirectory contains a complete, domain-specific RAG application that demonstrates how to effectively leverage RAG for real-world use cases.

## Project Structure

The repository is organized into domain-specific directories:

### 🏭 Energy Domain (`/energy`)
A RAG-powered application focused on energy sector maintenance and operations:
- Equipment maintenance scheduling and monitoring
- Intelligent query system for maintenance documentation
- Interactive dashboard for maintenance insights

### 🏘️ Real Estate Domain (`/realestate`)
A RAG implementation for real estate document analysis:
- Property agreement analysis
- Document querying system
- Interactive data visualization

## Features

- **Domain-Specific RAG Implementations**: Each domain showcases tailored RAG solutions
- **Interactive Web Interfaces**: Built with Streamlit for user-friendly interaction
- **Document Processing**: Efficient ingestion and processing of domain-specific documents
- **Intelligent Querying**: Natural language querying powered by OpenAI
- **Visualization**: Interactive data visualization using Plotly

## Prerequisites

- Python 3.8+
- OpenAI API key
- Required Python packages (specified in each domain's `requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/RAG-Domains-Adopters.git
   cd RAG-Domains-Adopters
   ```

2. Set up environment for specific domain:
   ```bash
   cd <domain-directory>  # energy or realestate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.template` to `.env`
   - Add your OpenAI API key to `.env`

## Usage

Each domain has its own application that can be run independently:

### Energy Domain
```bash
cd energy
streamlit run app.py
```

### Real Estate Domain
```bash
cd realestate
streamlit run app.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

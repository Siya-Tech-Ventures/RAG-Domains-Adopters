import streamlit as st
from financial_rag import FinancialRAG
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="Financial ESG Analysis",
    page_icon="💹",
    layout="wide"
)

# Initialize session state
if 'rag' not in st.session_state:
    st.session_state.rag = FinancialRAG()
if 'knowledge_base_created' not in st.session_state:
    st.session_state.knowledge_base_created = False

# Title and description
st.title("Financial ESG Analysis Dashboard 💹")
st.markdown("""
This application helps you analyze companies based on their ESG (Environmental, Social, and Governance) practices
using SEC filings, news articles, and stock information.
""")

# Sidebar for company input
with st.sidebar:
    st.header("Company Information")
    company_ticker = st.text_input("Enter Company Ticker (e.g., AAPL)").upper()
    company_name = st.text_input("Enter Company Name (e.g., Apple)")
    
    if st.button("Create Knowledge Base"):
        if company_ticker and company_name:
            with st.spinner("Creating knowledge base... This might take a minute..."):
                try:
                    st.session_state.rag.create_knowledge_base(company_ticker, company_name)
                    st.session_state.knowledge_base_created = True
                    st.success("Knowledge base created successfully!")
                except Exception as e:
                    st.error(f"Error creating knowledge base: {str(e)}")
        else:
            st.warning("Please enter both company ticker and name.")

# Main content area
if st.session_state.knowledge_base_created:
    # Query Categories
    st.header("Ask Questions")
    query_category = st.selectbox(
        "Select a category for your question:",
        ["ESG Overview", "Environmental", "Social", "Governance", "Financial Performance", "Custom Question"]
    )

    # Predefined questions based on category
    if query_category == "Custom Question":
        query = st.text_input(
            "Enter your question:",
            placeholder="Type your question here..."
        )
    else:
        questions = {
            "ESG Overview": [
                f"What are {company_name}'s main ESG initiatives and commitments?",
                f"What is {company_name}'s overall approach to sustainability?",
                f"How does {company_name} report its ESG metrics?",
                f"What are the key ESG risks and opportunities for {company_name}?"
            ],
            "Environmental": [
                f"What are {company_name}'s environmental initiatives and goals?",
                f"How does {company_name} manage its carbon footprint?",
                f"What renewable energy commitments has {company_name} made?",
                f"How does {company_name} handle waste management and recycling?"
            ],
            "Social": [
                f"What are {company_name}'s diversity and inclusion initiatives?",
                f"How does {company_name} manage its supply chain responsibility?",
                f"What community engagement programs does {company_name} have?",
                f"How does {company_name} ensure fair labor practices?"
            ],
            "Governance": [
                f"What is {company_name}'s board structure and diversity?",
                f"How does {company_name} handle business ethics?",
                f"What are {company_name}'s anti-corruption policies?",
                f"How transparent is {company_name}'s ESG reporting?"
            ],
            "Financial Performance": [
                f"What is {company_name}'s current market position?",
                f"How does {company_name}'s ESG performance impact its financial results?",
                f"What are {company_name}'s key financial metrics?",
                f"How does {company_name}'s sustainability initiatives affect its business model?"
            ]
        }
        query = st.selectbox("Select a question:", questions[query_category])
    
    if query:
        with st.spinner("Analyzing..."):
            try:
                response = st.session_state.rag.query_knowledge_base(query)
                st.markdown("### Answer")
                st.write(response)
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")
        
        # Option to analyze greenwashing
        if st.button("Analyze Greenwashing"):
            with st.spinner("Analyzing potential greenwashing..."):
                try:
                    greenwashing_analysis = st.session_state.rag.analyze_greenwashing(company_name)
                    st.markdown("### Greenwashing Analysis")
                    st.write(greenwashing_analysis)
                except Exception as e:
                    st.error(f"Error analyzing greenwashing: {str(e)}")
else:
    st.info("👈 Please enter company information and create a knowledge base to start analyzing.")

import os
from typing import List
from dotenv import load_dotenv
import yfinance as yf
from sec_api import QueryApi
from newsapi import NewsApiClient
import pandas as pd
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class FinancialRAG:
    def __init__(self):
        logger.info("Initializing FinancialRAG")
        try:
            self.sec_api = QueryApi(api_key=os.getenv('SEC_API_KEY'))
            self.news_api = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
            self.embeddings = OpenAIEmbeddings()
            self.llm = OpenAI(
                temperature=0.1,
                model="gpt-3.5-turbo-instruct"
            )
            # Create a directory for Chroma DB
            self.persist_directory = os.path.join(os.path.dirname(__file__), 'chroma_db')
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialize vector store with persistent storage
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            logger.info("Successfully initialized FinancialRAG")
        except Exception as e:
            logger.error(f"Error initializing FinancialRAG: {str(e)}")
            raise
        
    def fetch_sec_filings(self, company_ticker: str) -> List[str]:
        """Fetch SEC filings for ESG and sustainability related information"""
        logger.info(f"Fetching SEC filings for {company_ticker}")
        try:
            query = {
                "query": f"ticker:{company_ticker} AND (ESG OR sustainability OR environmental OR social OR governance)",
                "from": "0",
                "size": "10"
            }
            filings = self.sec_api.get_filings(query)
            results = [filing['description'] for filing in filings['filings']]
            logger.info(f"Successfully fetched {len(results)} SEC filings")
            return results
        except Exception as e:
            logger.error(f"Error fetching SEC filings: {str(e)}")
            raise

    def fetch_news_articles(self, company_name: str) -> List[str]:
        """Fetch relevant news articles about company's ESG practices"""
        logger.info(f"Fetching news articles for {company_name}")
        try:
            news = self.news_api.get_everything(
                q=f'{company_name} ESG sustainability environmental social governance',
                language='en',
                sort_by='relevancy',
                page_size=10
            )
            results = [article['description'] for article in news['articles']]
            logger.info(f"Successfully fetched {len(results)} news articles")
            return results
        except Exception as e:
            logger.error(f"Error fetching news articles: {str(e)}")
            raise

    def fetch_stock_info(self, ticker: str) -> str:
        """Fetch company's stock information and fundamental data"""
        logger.info(f"Fetching stock info for {ticker}")
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            company_profile = [
                f"Company: {info.get('longName', '')}",
                f"Industry: {info.get('industry', 'N/A')}",
                f"Sector: {info.get('sector', 'N/A')}",
                f"Business Summary: {info.get('longBusinessSummary', 'N/A')}",
                f"Market Cap: {info.get('marketCap', 'N/A')}",
                f"Revenue Growth: {info.get('revenueGrowth', 'N/A')}",
                f"Number of Employees: {info.get('fullTimeEmployees', 'N/A')}"
            ]
            
            result = "\n".join(company_profile)
            logger.info("Successfully fetched stock information")
            return result
        except Exception as e:
            logger.error(f"Error fetching stock information: {str(e)}")
            raise

    def create_knowledge_base(self, company_ticker: str, company_name: str):
        """Create and populate the vector store with company data"""
        logger.info(f"Creating knowledge base for {company_name} ({company_ticker})")
        try:
            # Gather all relevant data
            sec_data = self.fetch_sec_filings(company_ticker)
            news_data = self.fetch_news_articles(company_name)
            stock_data = self.fetch_stock_info(company_ticker)
            
            # Combine all data sources
            all_texts = sec_data + news_data + [stock_data]
            
            # Create text splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            
            # Split texts into chunks
            logger.info("Splitting texts into chunks")
            docs = text_splitter.create_documents(all_texts)
            
            # Add documents to vector store
            logger.info("Adding documents to vector store")
            self.vector_store.add_documents(docs)
            logger.info("Successfully created knowledge base")
        except Exception as e:
            logger.error(f"Error creating knowledge base: {str(e)}")
            raise

    def analyze_greenwashing(self, company_name: str) -> str:
        """Analyze potential greenwashing in company's ESG practices"""
        logger.info(f"Analyzing greenwashing for {company_name}")
        try:
            if not self.vector_store:
                logger.error("Vector store not initialized. Please create knowledge base first.")
                raise ValueError("Vector store not initialized. Please create knowledge base first.")
            
            # Create retriever
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            # Create chain
            chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True
            )
            
            # Define the analysis prompt
            prompt = f"""
            Analyze {company_name}'s ESG practices and identify potential greenwashing.
            Consider:
            1. Consistency between environmental claims and actions
            2. Specificity and measurability of ESG goals
            3. Transparency in reporting
            4. Third-party verification of claims
            5. Overall authenticity of sustainability initiatives
            
            Provide a detailed analysis with specific examples.
            """
            
            logger.info("Running analysis chain")
            # Run the chain
            result = chain.invoke({"query": prompt})
            logger.info("Successfully completed greenwashing analysis")
            return result['result']
        except Exception as e:
            logger.error(f"Error analyzing greenwashing: {str(e)}")
            raise

    def query_knowledge_base(self, query: str) -> str:
        """Query the knowledge base with a specific question"""
        logger.info(f"Querying knowledge base with: {query}")
        try:
            if not self.vector_store:
                logger.error("Vector store not initialized. Please create knowledge base first.")
                raise ValueError("Vector store not initialized. Please create knowledge base first.")
            
            # Create retriever
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            # Create custom prompt template
            template = """Use the following pieces of context to answer the question. If you don't know the answer, just say that you don't know, don't try to make up an answer.

            Context: {context}

            Question: {question}
            Answer: """

            QA_CHAIN_PROMPT = PromptTemplate(
                input_variables=["context", "question"],
                template=template,
            )

            # Create chain
            chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
                return_source_documents=True
            )
            
            logger.info("Running query chain")
            # Run the chain
            result = chain.invoke({"query": query})
            logger.info("Successfully executed query")
            return result['result']
        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    rag = FinancialRAG()
    rag.create_knowledge_base("AAPL", "Apple")
    analysis = rag.analyze_greenwashing("Apple")
    print(analysis)

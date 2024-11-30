import os
from typing import List, Dict, Any, Optional
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
import pandas as pd
import numpy as np
from datetime import datetime

class FinanceRAG:
    def __init__(self, docs_dir: str, performance_data_path: str = None):
        """
        Initialize the RAG system for finance domain.
        
        Args:
            docs_dir: Directory containing processed documentation
            performance_data_path: Path to historical performance data (CSV)
        """
        self.docs_dir = docs_dir
        self.performance_data_path = performance_data_path
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        self.vector_stores = {}
        self.qa_chains = {}
        self.performance_data = None
        
        # Create persistent directory for ChromaDB
        self.chroma_dir = os.path.join(os.path.dirname(docs_dir), "chroma_db")
        os.makedirs(self.chroma_dir, exist_ok=True)
        
    def load_documentation(self):
        """Load and process documentation by category."""
        categories = [
            "market_analysis",
            "financial_reports",
            "investment_strategies",
            "risk_management"
        ]
        
        for category in categories:
            category_dir = os.path.join(self.docs_dir, category)
            if os.path.exists(category_dir):
                # Load documents for this category
                loader = DirectoryLoader(category_dir, glob="**/*.txt", loader_cls=TextLoader)
                documents = loader.load()
                texts = self.text_splitter.split_documents(documents)
                
                # Create vector store for this category with persistent storage
                persist_dir = os.path.join(self.chroma_dir, f"finance_{category}")
                self.vector_stores[category] = Chroma.from_documents(
                    documents=texts,
                    embedding=self.embeddings,
                    collection_name=f"finance_{category}",
                    persist_directory=persist_dir
                )
                
                # Create QA chain for this category
                self.qa_chains[category] = RetrievalQA.from_chain_type(
                    llm=ChatOpenAI(temperature=0),
                    chain_type="stuff",
                    retriever=self.vector_stores[category].as_retriever()
                )
    
    def query_documentation(self, query: str, category: Optional[str] = None) -> str:
        """
        Query the documentation with category-specific context.
        
        Args:
            query: User's question
            category: Optional category to focus the search
            
        Returns:
            Answer based on the relevant documentation
        """
        if not self.qa_chains:
            raise ValueError("Documentation not loaded. Call load_documentation() first.")
        
        if category and category in self.qa_chains:
            # Query specific category
            return self.qa_chains[category].run(query)
        else:
            # Query all categories and combine results
            all_answers = []
            for cat, chain in self.qa_chains.items():
                try:
                    answer = chain.run(query)
                    all_answers.append(f"{cat.replace('_', ' ').title()}: {answer}")
                except Exception as e:
                    print(f"Error querying {cat}: {str(e)}")
            
            return "\n\n".join(all_answers)
    
    def get_available_categories(self) -> List[str]:
        """Get list of available document categories."""
        return list(self.qa_chains.keys())

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

class EnergyMaintenanceRAG:
    def __init__(self, docs_dir: str, performance_data_path: str = None):
        """
        Initialize the RAG system for energy maintenance prediction.
        
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
            "equipment_health",
            "maintenance_schedule",
            "technical_documentation",
            "data_ingestion"
        ]
        
        for category in categories:
            category_dir = os.path.join(self.docs_dir, category)
            if os.path.exists(category_dir):
                # Load documents for this category
                loader = DirectoryLoader(category_dir, glob="**/*.txt", loader_cls=TextLoader)
                documents = loader.load()
                texts = self.text_splitter.split_documents(documents)
                
                # Create vector store for this category with persistent storage
                persist_dir = os.path.join(self.chroma_dir, f"energy_{category}")
                self.vector_stores[category] = Chroma.from_documents(
                    documents=texts,
                    embedding=self.embeddings,
                    collection_name=f"energy_{category}",
                    persist_directory=persist_dir
                )
                
                # Create QA chain for this category
                self.qa_chains[category] = RetrievalQA.from_chain_type(
                    llm=ChatOpenAI(temperature=0),
                    chain_type="stuff",
                    retriever=self.vector_stores[category].as_retriever()
                )
    
    def load_performance_data(self):
        """Load historical performance data if available."""
        if self.performance_data_path and os.path.exists(self.performance_data_path):
            self.performance_data = pd.read_csv(self.performance_data_path)
            
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
        
    def analyze_equipment_health(self, equipment_id: str) -> Dict[str, Any]:
        """
        Analyze equipment health based on performance data and documentation.
        
        Args:
            equipment_id: Unique identifier for the equipment
            
        Returns:
            Dict containing health analysis and maintenance recommendations
        """
        if self.performance_data is None:
            return {"error": "No performance data available"}
            
        # Filter data for specific equipment
        equipment_data = self.performance_data[
            self.performance_data['equipment_id'] == equipment_id
        ]
        
        if len(equipment_data) == 0:
            return {"error": f"No data found for equipment {equipment_id}"}
            
        # Calculate basic health metrics
        latest_readings = equipment_data.iloc[-1]
        historical_avg = equipment_data.mean()
        
        # Detect anomalies using simple statistical method
        std_dev = equipment_data.std()
        anomalies = abs(latest_readings - historical_avg) > (2 * std_dev)
        
        # Query documentation for relevant maintenance procedures
        if any(anomalies):
            maintenance_query = f"What are the maintenance procedures for {equipment_id} when showing abnormal readings in {', '.join(anomalies[anomalies].index)}?"
            maintenance_info = self.query_documentation(maintenance_query, category="equipment_health")
        else:
            maintenance_info = "No immediate maintenance required based on current readings."
            
        return {
            "equipment_id": equipment_id,
            "timestamp": datetime.now().isoformat(),
            "health_status": "warning" if any(anomalies) else "normal",
            "anomalies_detected": anomalies[anomalies].index.tolist(),
            "maintenance_recommendations": maintenance_info,
            "current_readings": latest_readings.to_dict(),
            "historical_averages": historical_avg.to_dict()
        }
        
    def predict_maintenance_schedule(self, equipment_id: str) -> Dict[str, Any]:
        """
        Generate a predictive maintenance schedule based on equipment history.
        
        Args:
            equipment_id: Unique identifier for the equipment
            
        Returns:
            Dict containing maintenance schedule and predictions
        """
        if self.performance_data is None:
            return {"error": "No performance data available"}
            
        equipment_data = self.performance_data[
            self.performance_data['equipment_id'] == equipment_id
        ]
        
        if len(equipment_data) == 0:
            return {"error": f"No data found for equipment {equipment_id}"}
            
        # Calculate time since last maintenance
        last_maintenance = equipment_data['last_maintenance'].max()
        current_time = datetime.now()
        time_since_maintenance = (current_time - pd.to_datetime(last_maintenance)).days
        
        # Simple prediction based on historical patterns
        avg_maintenance_interval = equipment_data['maintenance_interval'].mean()
        
        return {
            "equipment_id": equipment_id,
            "last_maintenance": last_maintenance,
            "days_since_maintenance": time_since_maintenance,
            "recommended_maintenance_interval": avg_maintenance_interval,
            "next_maintenance_due": (pd.to_datetime(last_maintenance) + 
                                   pd.Timedelta(days=avg_maintenance_interval)).isoformat(),
            "maintenance_priority": "high" if time_since_maintenance > avg_maintenance_interval else "normal"
        }

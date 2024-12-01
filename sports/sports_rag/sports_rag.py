from typing import List, Dict
import os
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.schema import Document
import google.generativeai as genai
from .cricket_data_loader import process_all_matches, load_cricket_match
import json
from pathlib import Path
import uuid
import datetime

class SportsRAG:
    def __init__(self, data_dir: str, google_api_key: str):
        """
        Initialize the Sports RAG system
        
        Args:
            data_dir (str): Directory containing sports data documents
            google_api_key (str): Google API key for Gemini Pro
        """
        self.data_dir = data_dir
        self.documents = []
        os.environ["GOOGLE_API_KEY"] = google_api_key
        genai.configure(api_key=google_api_key)
        
        # Configure Gemini Pro model
        self.model = genai.GenerativeModel('gemini-pro')
        
    def load_documents(self) -> List[Document]:
        """Load documents from the data directory"""
        # Process cricket match data
        cricket_matches = process_all_matches(self.data_dir)
        self.documents = cricket_matches
        return cricket_matches
    
    def initialize_vector_store(self, documents: List[Document]):
        """Kept for compatibility, does nothing now"""
        pass
        
    def _generate_prompt(self, question: str) -> str:
        """Generate a prompt for Gemini Pro"""
        context = "\n\n".join([match['text'] for match in self.documents])
        
        return f"""You are a cricket match analysis AI. Use the following match data to answer the question accurately.
        If the information is not available in the match data, say so clearly.
        
        Match Data:
        {context}

        Question: {question}

        Answer: Please provide a detailed answer based on the match data above. Include specific numbers and statistics when available."""
    
    def add_new_data(self, text_data: str, metadata: Dict) -> None:
        """
        Add new match data to the system
        
        Args:
            text_data (str): The match data text in JSON format
            metadata (Dict): Metadata about the match (teams, date, event, etc.)
        """
        try:
            # Parse the text data as JSON
            match_data = json.loads(text_data)
            
            # Create a temporary file to process the match data
            temp_file = Path(self.data_dir) / f"temp_{uuid.uuid4()}.json"
            with open(temp_file, 'w') as f:
                json.dump(match_data, f)
            
            # Process the match data using load_cricket_match
            processed_text = load_cricket_match(str(temp_file))
            
            # Create the final document
            new_doc = {
                'text': processed_text,
                'metadata': metadata
            }
            
            # Add to documents list
            self.documents.append(new_doc)
            
            # Generate random filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            random_id = str(uuid.uuid4())[:8]
            filename = f"match_{timestamp}_{random_id}.json"
            
            # Ensure the data directory exists
            data_dir = Path(self.data_dir)
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Save the original match data
            file_path = data_dir / filename
            with open(file_path, 'w') as f:
                json.dump(match_data, f, indent=2)
            
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()
                
        except json.JSONDecodeError:
            raise Exception("Invalid JSON format in text_data")
        except Exception as e:
            raise Exception(f"Failed to save match data: {str(e)}")
    
    def query(self, question: str) -> Dict:
        """
        Query the system with cricket-related questions
        
        Args:
            question (str): Question about match details, statistics, players, etc.
            
        Returns:
            Dict containing the response
        """
        try:
            # Generate prompt with all match data
            prompt = self._generate_prompt(question)
            
            # Get response from Gemini Pro
            response = self.model.generate_content(prompt)
            
            return {
                "answer": response.text,
                "source_documents": [doc['metadata'] for doc in self.documents]
            }
            
        except Exception as e:
            return {
                "answer": f"Error generating response: {str(e)}",
                "source_documents": []
            }

import PyPDF2
from bs4 import BeautifulSoup
import requests
import os
from typing import List, Dict, Union
import json
import pandas as pd

class DocumentProcessor:
    """Handles the processing of various document types for real estate data"""
    
    @staticmethod
    def process_pdf(file_path: str) -> str:
        """
        Extract text from PDF file with enhanced handling for legal documents
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from PDF
        """
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = []
            
            # Extract metadata if available
            metadata = reader.metadata
            if metadata:
                text.append("Document Metadata:")
                for key, value in metadata.items():
                    if value:
                        text.append(f"{key}: {value}")
                text.append("\n")
            
            # Extract text from each page with page numbers
            for i, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    text.append(f"Page {i}:")
                    text.append(page_text)
                    text.append("\n")
            
            return "\n".join(text)

    @staticmethod
    def process_text(file_path: str) -> str:
        """
        Read text from file
        
        Args:
            file_path (str): Path to the text file
            
        Returns:
            str: Content of text file
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
            
    @staticmethod
    def process_csv(file_path: str) -> str:
        """
        Process CSV file containing real estate data
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            str: Formatted text content from CSV
        """
        df = pd.read_csv(file_path)
        text_content = []
        
        for _, row in df.iterrows():
            # Convert row to dictionary and remove NaN values
            row_dict = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
            # Format each row as a property listing
            listing = "Property Listing:\n"
            for key, value in row_dict.items():
                listing += f"{key}: {value}\n"
            text_content.append(listing)
        
        return "\n\n".join(text_content)

    @staticmethod
    def process_listing_data(listing_data: Dict) -> str:
        """
        Process structured listing data into text format
        
        Args:
            listing_data (dict): Dictionary containing listing information
            
        Returns:
            str: Formatted text representation of listing
        """
        template = """
Property Listing Information:
Address: {address}
Price: ${price:,}
Bedrooms: {bedrooms}
Bathrooms: {bathrooms}
Square Footage: {sqft:,} sq ft
Property Type: {property_type}
Year Built: {year_built}
Description: {description}
Features: {features}
        """
        return template.format(**listing_data)

    @staticmethod
    def process_legal_document(file_path: str) -> Dict[str, str]:
        """
        Process legal documents with special handling for different sections
        
        Args:
            file_path (str): Path to the legal document
            
        Returns:
            dict: Processed document with sections
        """
        extension = file_path.lower().split('.')[-1]
        
        if extension == 'pdf':
            text = DocumentProcessor.process_pdf(file_path)
        else:
            text = DocumentProcessor.process_text(file_path)
        
        # Basic section identification (can be enhanced based on specific document types)
        sections = {
            "full_text": text,
            "parties_involved": "",
            "terms_and_conditions": "",
            "payment_terms": "",
            "termination_clauses": "",
            "signatures": ""
        }
        
        # Simple section identification based on common headers
        text_lower = text.lower()
        
        if "between" in text_lower or "parties" in text_lower:
            sections["parties_involved"] = text[:text.find("NOW THEREFORE")] if "NOW THEREFORE" in text else ""
            
        if "terms and conditions" in text_lower:
            start = text_lower.find("terms and conditions")
            end = text_lower.find("payment") if "payment" in text_lower else len(text)
            sections["terms_and_conditions"] = text[start:end]
            
        if "payment" in text_lower:
            start = text_lower.find("payment")
            end = text_lower.find("termination") if "termination" in text_lower else len(text)
            sections["payment_terms"] = text[start:end]
            
        if "termination" in text_lower:
            start = text_lower.find("termination")
            end = text_lower.find("in witness") if "in witness" in text_lower else len(text)
            sections["termination_clauses"] = text[start:end]
            
        if "in witness" in text_lower:
            sections["signatures"] = text[text_lower.find("in witness"):]
        
        return sections

    @staticmethod
    def scrape_listing(url: str) -> str:
        """
        Scrape real estate listing from URL
        
        Args:
            url (str): URL of the listing
            
        Returns:
            str: Scraped content
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text()
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return ""

class DataIngestion:
    """Manages the ingestion of real estate documents and data"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.processor = DocumentProcessor()
        os.makedirs(data_dir, exist_ok=True)

    def ingest_file(self, file_path: str) -> str:
        """
        Ingest a single file based on its type
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Processed text content
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self.processor.process_pdf(file_path)
        elif ext in ['.txt', '.md']:
            return self.processor.process_text(file_path)
        elif ext == '.csv':
            return self.processor.process_csv(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def ingest_directory(self, directory: str) -> List[str]:
        """
        Ingest all supported files in a directory
        
        Args:
            directory (str): Directory path
            
        Returns:
            list: List of processed text contents
        """
        documents = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.pdf', '.txt', '.md','.csv')):
                    file_path = os.path.join(root, file)
                    try:
                        content = self.ingest_file(file_path)
                        documents.append(content)
                    except Exception as e:
                        print(f"Error processing {file_path}: {str(e)}")
        return documents

    def ingest_listings(self, listings_data: List[Dict]) -> List[str]:
        """
        Ingest multiple listing data
        
        Args:
            listings_data (list): List of dictionaries containing listing information
            
        Returns:
            list: List of processed listing texts
        """
        return [self.processor.process_listing_data(listing) for listing in listings_data]

    def ingest_urls(self, urls: List[str]) -> List[str]:
        """
        Ingest content from multiple URLs
        
        Args:
            urls (list): List of URLs to scrape
            
        Returns:
            list: List of scraped contents
        """
        return [self.processor.scrape_listing(url) for url in urls if url.strip()]

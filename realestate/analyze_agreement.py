from ingestion import DocumentProcessor
from rag_engine import RealEstateRAG
import os

def analyze_rental_agreement(file_path):
    # Initialize the processor and RAG engine
    processor = DocumentProcessor()
    rag = RealEstateRAG()
    
    # Process the document
    print("Processing document...")
    document_sections = processor.process_legal_document(file_path)
    
    # Ingest the document into the RAG engine
    print("\nIngesting document...")
    rag.ingest_documents([document_sections["full_text"]])
    
    # Analyze the document
    print("\nAnalyzing document...")
    analysis = rag.analyze_legal_document(document_sections["full_text"])
    
    # Print analysis results
    print("\n=== RENTAL AGREEMENT ANALYSIS ===\n")
    
    for question, answer in analysis.items():
        print(f"\n{question}")
        print("-" * len(question))
        print(f"{answer}\n")
        print("-" * 80)

if __name__ == "__main__":
    # Get the absolute path to the sample rental agreement
    current_dir = os.path.dirname(os.path.abspath(__file__))
    agreement_path = os.path.join(current_dir, "sample_documents", "rental_agreement.txt")
    
    # Analyze the agreement
    analyze_rental_agreement(agreement_path)

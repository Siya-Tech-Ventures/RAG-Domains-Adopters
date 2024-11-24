import os
from sports_rag import SportsRAG
from dotenv import load_dotenv

load_dotenv()
def test_cricket_rag():
    # Get the Google API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        return
    
    # Initialize the RAG system
    rag = SportsRAG(data_dir="data", google_api_key=api_key)
    
    try:
        # Load and process documents
        print("Loading documents...")
        documents = rag.load_documents()
        print(f"Loaded {len(documents)} document chunks")
        
        # Initialize vector store
        print("\nInitializing vector store...")
        rag.initialize_vector_store(documents)
        
        # Test some cricket-specific queries
        test_queries = [
            "How many runs were scored in the match between Jamaica and Windward Islands?",
            "What was the result of the match between Trinidad and Tobago vs Leeward Islands?",
            "Who won the toss in the match between Jamaica and Barbados?",
            "List all the sixes hit in any match",
            "Which team had the highest score in any single innings?"
        ]
        
        print("\nTesting queries:")
        for query in test_queries:
            print(f"\nQuery: {query}")
            try:
                response = rag.query(query)
                print("Answer:", response["answer"])
                print("\nContext used:")
                print(response["context"])
                print("-" * 80)
            except Exception as e:
                print(f"Error processing query: {str(e)}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_cricket_rag()

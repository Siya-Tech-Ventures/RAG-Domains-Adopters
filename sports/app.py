import streamlit as st
import os
from sports_rag import SportsRAG
import tempfile
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def initialize_rag_system(api_key=None):
    """Initialize the RAG system with cricket match data."""
    # Use provided API key or get from environment
    google_api_key = api_key or os.getenv("GOOGLE_API_KEY")
    
    # Get the absolute path to the data directory
    current_dir = Path(__file__).parent
    data_dir = current_dir / "data"
    
    if not data_dir.exists():
        st.error(f"Data directory not found at {data_dir}")
        st.stop()
    
    # Initialize RAG system
    try:
        rag = SportsRAG(data_dir=str(data_dir), google_api_key=google_api_key)
        with st.spinner("Loading cricket match data..."):
            # Show progress for data loading
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Load and process documents
            status_text.text("Loading match files...")
            documents = rag.load_documents()
            progress_bar.progress(50)
            
            # Initialize vector store
            status_text.text("Initializing vector store...")
            rag.initialize_vector_store(documents)
            progress_bar.progress(100)
            
            # Clean up progress indicators
            progress_bar.empty()
            status_text.empty()
            
            st.success(f"Successfully loaded {len(documents)} cricket matches!")
            return rag
            
    except Exception as e:
        st.error(f"Error initializing RAG system: {str(e)}")
        return None

def main():
    st.title("Cricket Match Analysis RAG System")
    st.markdown("""
    A Retrieval-Augmented Generation (RAG) system for cricket match analysis, powered by Google Gemini Pro.
    Ask questions about matches, players, statistics, and tactical decisions.
    """)

    # Check for API key in environment
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Show API key input if not in environment
    if not api_key:
        st.sidebar.title("Configuration")
        api_key = st.sidebar.text_input("Enter Google API Key", type="password")
        if not api_key:
            st.warning("Please enter your Google API key in the sidebar or set GOOGLE_API_KEY in .env file to continue.")
            st.stop()
        os.environ["GOOGLE_API_KEY"] = api_key

    # Initialize session state with API key
    if 'rag' not in st.session_state:
        st.session_state.rag = initialize_rag_system(api_key if not os.getenv("GOOGLE_API_KEY") else None)
    
    if not st.session_state.rag:
        st.error("Failed to initialize the RAG system. Please check your API key and try again.")
        st.stop()

    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Query Matches", "Add Match Data", "Upload Match File"])

    # Query System Tab
    with tab1:
        st.header("Query Cricket Matches")
        st.markdown("""
        Ask questions about:
        - Match results and scores
        - Player performances
        - Key events (boundaries, wickets)
        - Match statistics
        - Tactical analysis
        """)
        
        # Add example queries in an expander
        with st.expander("See example queries"):
            st.markdown("""
            - How many runs were scored in the match between Jamaica and Windward Islands?
            - What was the result of the match between Trinidad and Tobago vs Leeward Islands?
            - Who won the toss in the match between Jamaica and Barbados?
            - List all the sixes hit in any match
            - Which team had the highest score in any single innings?
            """)
        
        question = st.text_area("Enter your question:", 
                              placeholder="E.g., What was the final score in the match between Jamaica and Windward Islands?")
        
        if st.button("Get Answer"):
            if question:
                try:
                    with st.spinner("Analyzing with Gemini Pro..."):
                        response = st.session_state.rag.query(question)
                        
                        # Display the answer in a nice format
                        st.markdown("### Answer")
                        st.write(response["answer"])
                        
                        # Show the source documents in an expander
                        with st.expander("View Source Documents"):
                            st.markdown("### Source Match Data")
                            for doc in response["source_documents"]:
                                st.write(doc)
                            
                            # Show metadata if available
                            if "metadata" in response:
                                st.markdown("### Match Details")
                                metadata = response["metadata"]
                                st.write(f"- Event: {metadata.get('event', 'N/A')}")
                                st.write(f"- Teams: {metadata.get('teams', 'N/A')}")
                                st.write(f"- Date: {metadata.get('date', 'N/A')}")
                                st.write(f"- Venue: {metadata.get('venue', 'N/A')}")
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
            else:
                st.warning("Please enter a question")

    # Add Text Data Tab
    with tab2:
        st.header("Add New Match Data")
        
        # Input fields for match data
        teams = st.multiselect("Select Teams", ["Team A", "Team B", "Team C"], max_selections=2)
        match_date = st.date_input("Match Date")
        event_name = st.text_input("Event Name")
        
        # Match details in JSON format
        st.markdown("""
        Enter match data in JSON format following this structure:
        ```json
        {
            "info": {
                "teams": ["Team A", "Team B"],
                "dates": ["2024-01-01"],
                "venue": "Stadium Name",
                "event": {"name": "Tournament Name"},
                "match_type": "T20",
                "toss": {
                    "winner": "Team A",
                    "decision": "bat"
                },
                "players": {
                    "Team A": ["Player 1", "Player 2"],
                    "Team B": ["Player 3", "Player 4"]
                }
            }
        }
        ```
        """)
        
        text_data = st.text_area("Match Data (JSON format)", height=300)
        
        if st.button("Add Match Data"):
            if text_data and teams:
                try:
                    with st.spinner("Processing match data..."):
                        metadata = {
                            "sport": "cricket",
                            "teams": teams,
                            "event": event_name,
                            "date": str(match_date)
                        }
                        
                        st.session_state.rag.add_new_data(text_data, metadata)
                        st.success("Match data added successfully!")
                except Exception as e:
                    st.error(f"Error adding data: {str(e)}")
            else:
                st.warning("Please enter match data and teams")

    # Upload File Tab
    with tab3:
        st.header("Upload Match Data File")
        
        # Show format instructions
        st.markdown("""
        ### File Format Instructions
        Upload a JSON file containing match data in the following format:
        ```json
        {
            "info": {
                "teams": ["Team A", "Team B"],
                "dates": ["2024-01-01"],
                "venue": "Stadium Name",
                "event": {
                    "name": "Tournament Name",
                    "match_number": "1"
                },
                "match_type": "T20",
                "toss": {
                    "winner": "Team A",
                    "decision": "bat"
                },
                "players": {
                    "Team A": ["Player 1", "Player 2", "..."],
                    "Team B": ["Player 3", "Player 4", "..."]
                },
                "officials": {
                    "umpires": ["Umpire 1", "Umpire 2"],
                    "match_referees": ["Referee 1"]
                }
            },
            "innings": [
                {
                    "team": "Team A",
                    "overs": [...],
                    "powerplays": [...],
                    "target": {...}
                }
            ]
        }
        ```
        """)
        
        # Add sample file download
        st.markdown("""
        ### Sample File
        You can download a sample match data file to see the exact format:
        - [Download sample template](https://raw.githubusercontent.com/Siya-Tech-Ventures/RAG-Domains-Adopters/refs/heads/main/sports/data/wi_211976.json)
        """)
        
        st.markdown("---")
        
        uploaded_file = st.file_uploader("Choose a match data file", type=['json'])
        
        if uploaded_file is not None:
            try:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name

                # Add to RAG system
                with st.spinner("Processing match file..."):
                    st.session_state.rag.add_new_data(
                        open(tmp_file_path).read(),
                        {"filename": uploaded_file.name, "format": "json"}
                    )
                    st.success(f"File {uploaded_file.name} processed successfully!")

                # Clean up
                os.unlink(tmp_file_path)
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

    # Add footer with information about the data
    st.markdown("---")
    st.markdown("### About the Data")
    st.markdown("""
    This system contains cricket match data from the Super 50 tournament, including:
    - Ball-by-ball analysis
    - Match results and statistics
    - Player performances
    - Key events and moments
    
    The data is processed using Google's Gemini Pro AI model to provide accurate and contextual responses to your queries.
    """)

if __name__ == "__main__":
    main()

import streamlit as st
import os
from sports_rag import SportsRAG
import tempfile
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def initialize_rag_system():
    """Initialize the RAG system with cricket match data."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("GOOGLE_API_KEY environment variable not set")
        st.stop()
    
    # Get the absolute path to the data directory
    current_dir = Path(__file__).parent
    data_dir = current_dir / "data"
    
    if not data_dir.exists():
        st.error(f"Data directory not found at {data_dir}")
        st.stop()
    
    # Initialize RAG system
    try:
        rag = SportsRAG(data_dir=str(data_dir), google_api_key=api_key)
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
        st.stop()

# Initialize session state
if 'rag' not in st.session_state:
    st.session_state.rag = initialize_rag_system()

def main():
    st.title("Cricket Match Analysis RAG System")
    st.markdown("""
    A Retrieval-Augmented Generation (RAG) system for cricket match analysis, powered by Google Gemini Pro.
    Ask questions about matches, players, statistics, and tactical decisions.
    """)

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
                        
                        # Show the context in an expander
                        with st.expander("View Match Context"):
                            st.markdown("### Retrieved Match Data")
                            st.write(response["context"])
                            
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
        text_data = st.text_area("Enter match analysis or statistics:", 
                                height=200,
                                placeholder="Enter match details, player statistics, or tactical observations...")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            teams = st.text_input("Teams", placeholder="e.g., Team A vs Team B")
        with col2:
            event_name = st.text_input("Tournament/Event", placeholder="e.g., Super 50")
        with col3:
            match_date = st.date_input("Match Date")
        
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
        uploaded_file = st.file_uploader("Choose a match data file", type=['txt', 'json'])
        
        if uploaded_file is not None:
            try:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{uploaded_file.name.split(".")[-1]}') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name

                # Add to RAG system
                with st.spinner("Processing match file..."):
                    if uploaded_file.name.endswith('.json'):
                        # For JSON files, we'll use the cricket data loader
                        st.session_state.rag.add_new_data(
                            open(tmp_file_path).read(),
                            {"filename": uploaded_file.name, "format": "json"}
                        )
                    else:
                        # For text files, process normally
                        content = uploaded_file.getvalue().decode()
                        st.session_state.rag.add_new_data(
                            content,
                            {"filename": uploaded_file.name, "format": "text"}
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

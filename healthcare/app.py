import streamlit as st
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, PDFMinerLoader
from langchain.document_loaders.merge import MergedDataLoader
import os
from dotenv import load_dotenv
import glob
import random

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

class HealthcareRAGBot:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self.document_topics = []
        
    def load_documents(self, data_dir):
        """Load both PDF and text documents from the directory"""
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize loaders for different file types
        txt_loader = DirectoryLoader(
            data_dir,
            glob="**/*.txt",
            loader_cls=TextLoader
        )
        
        pdf_loader = DirectoryLoader(
            data_dir,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )
        
        # Load documents from both loaders
        txt_docs = txt_loader.load() if glob.glob(os.path.join(data_dir, "**/*.txt"), recursive=True) else []
        pdf_docs = pdf_loader.load() if glob.glob(os.path.join(data_dir, "**/*.pdf"), recursive=True) else []
        
        # Combine documents
        all_docs = txt_docs + pdf_docs
        
        if not all_docs:
            st.warning("No documents found in the data directory. Please add .txt or .pdf files.")
            return []
            
        return all_docs
        
    def initialize_vector_store(self, data_dir="./data"):
        """Initialize the vector store with documents"""
        try:
            # Load all documents
            documents = self.load_documents(data_dir)
            
            if not documents:
                return
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""],
                length_function=len
            )
            texts = text_splitter.split_documents(documents)

            # Create vector store
            self.vector_store = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            
            # Generate document topics for suggested questions
            self.generate_document_topics(texts)
            
            st.success(f"Successfully processed {len(documents)} documents into {len(texts)} chunks.")
            
        except Exception as e:
            st.error(f"Error initializing vector store: {str(e)}")

    def generate_document_topics(self, texts):
        """Generate main topics from the documents for question suggestions"""
        try:
            # Combine more text chunks for better topic analysis
            sample_size = min(10, len(texts))  # Increased sample size
            sample_texts = random.sample(texts, sample_size)
            combined_text = "\n".join([text.page_content for text in sample_texts])
            
            prompt = f"""As a healthcare regulatory compliance expert, analyze the following healthcare document content and generate 5 specific questions that can be answered using ONLY this content.
            Focus on the actual information present in the text.
            
            Requirements for the questions:
            1. Each question must be directly answerable from the given content
            2. Use specific terms, regulations, or procedures mentioned in the text
            3. Avoid general questions that might not be covered in the content
            4. Include the relevant section or topic from the text in the question
            
            Text: {combined_text}

            Format your response as:
            1. [First specific question based on actual content]
            2. [Second specific question based on actual content]
            etc.
            """
            
            response = self.model.generate_content(prompt)
            # Clean and format questions
            questions = [q.strip().split('. ', 1)[-1] for q in response.text.split('\n') 
                       if q.strip() and '?' in q and any(char.isdigit() for char in q)]
            self.document_topics = questions[:5]  # Keep top 5 questions
            
        except Exception as e:
            st.error(f"Error generating topic suggestions: {str(e)}")
            self.document_topics = []

    def get_relevant_context(self, query, k=5):
        """Retrieve relevant documents for the query"""
        if not self.vector_store:
            return []
        
        try:
            # Increase the number of retrieved documents for better context
            docs = self.vector_store.similarity_search(query, k=k)
            
            # Sort documents by relevance score if available
            context_parts = []
            for doc in docs:
                # Add document title or source if available
                source_info = f"\nSource: {doc.metadata.get('source', 'Unknown')}" if hasattr(doc, 'metadata') else ""
                context_parts.append(f"{doc.page_content}{source_info}")
            
            return "\n\n---\n\n".join(context_parts)
        except Exception as e:
            st.error(f"Error retrieving context: {str(e)}")
            return []

    def get_suggested_questions(self):
        """Return suggested questions based on document content"""
        return self.document_topics

    def get_response(self, query):
        """Generate response using RAG with Gemini Pro"""
        # Get relevant context
        context = self.get_relevant_context(query)
        
        if not context:
            return {
                "answer": "I apologize, but I don't have enough context to answer your question. Please make sure there are documents loaded in the data directory.",
                "context": ""
            }
        
        # Construct prompt
        prompt = f"""As a healthcare regulatory compliance expert, carefully analyze the following context and question.
        Provide a detailed answer ONLY if the information is explicitly present in the context.
        If the specific information is not in the context, respond with: "I apologize, but I cannot find specific information about [topic] in the provided documents."

        Context: {context}

        Question: {query}

        Instructions:
        1. Only answer with information directly supported by the context
        2. Quote specific regulations or guidelines when relevant
        3. If the answer requires information not in the context, acknowledge what's missing
        4. Provide section references when possible

        Answer:"""

        # Generate response
        response = self.model.generate_content(prompt)
        
        return {
            "answer": response.text,
            "context": context
        }

def main():
    st.set_page_config(page_title="Healthcare Regulatory Compliance Assistant")
    st.title("Healthcare Regulatory Compliance Assistant")

    # Initialize bot if not exists
    if "bot" not in st.session_state:
        st.session_state.bot = HealthcareRAGBot()
        st.session_state.bot.initialize_vector_store()

    # Add file uploader
    uploaded_files = st.file_uploader(
        "Upload regulatory documents (PDF or TXT)",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    # Save uploaded files and reinitialize bot
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join("data", uploaded_file.name)
            os.makedirs("data", exist_ok=True)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success("Files uploaded successfully!")
        
        # Reinitialize bot with new documents
        st.session_state.bot = HealthcareRAGBot()
        st.session_state.bot.initialize_vector_store()

    # Display suggested questions
    suggested_questions = st.session_state.bot.get_suggested_questions()
    if suggested_questions:
        with st.expander("📝 Suggested Questions", expanded=True):
            st.write("Based on your documents, you might want to ask:")
            for question in suggested_questions:
                if st.button(f"🔍 {question}", key=question):
                    st.session_state.messages.append({"role": "user", "content": question})
                    with st.chat_message("user"):
                        st.markdown(question)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about healthcare regulations..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            response_dict = st.session_state.bot.get_response(prompt)
            st.markdown(response_dict["answer"])
            
            # Show context in expander
            with st.expander("View Source Context"):
                st.markdown(response_dict["context"])
                
        st.session_state.messages.append({"role": "assistant", "content": response_dict["answer"]})

if __name__ == "__main__":
    main()
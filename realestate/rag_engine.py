from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class RealEstateRAG:
    def __init__(self, persist_directory="./data/chroma"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.initialize_vectorstore()
        self.setup_qa_chain()

    def initialize_vectorstore(self):
        """Initialize or load the vector store"""
        if os.path.exists(self.persist_directory):
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )

    def setup_qa_chain(self):
        """Set up the QA chain with custom prompt"""
        template = """You are a knowledgeable real estate expert and legal analyst. Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        When analyzing legal documents, pay special attention to:
        1. Potential loopholes or ambiguous clauses
        2. Missing important terms or conditions
        3. Rights and obligations of all parties
        4. Payment terms and conditions
        5. Termination clauses
        6. Legal compliance issues

        {context}

        Question: {question}
        Expert Answer:"""

        QA_CHAIN_PROMPT = PromptTemplate(
            input_variables=["context", "question"],
            template=template,
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model_name="gpt-4", temperature=0),
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
            return_source_documents=True
        )

    def ingest_documents(self, documents):
        """
        Ingest documents into the vector store
        
        Args:
            documents (list): List of document texts to ingest
        """
        texts = self.text_splitter.create_documents(documents)
        self.vectorstore.add_documents(texts)
        self.vectorstore.persist()

    def query(self, question):
        """
        Query the RAG system
        
        Args:
            question (str): Question to ask
            
        Returns:
            dict: Contains answer and source documents
        """
        result = self.qa_chain({"query": question})
        return {
            "answer": result["result"],
            "sources": [doc.page_content for doc in result["source_documents"]]
        }

    def similarity_search(self, query, k=3):
        """
        Perform similarity search in the vector store
        
        Args:
            query (str): Query text
            k (int): Number of results to return
            
        Returns:
            list: List of similar documents
        """
        return self.vectorstore.similarity_search(query, k=k)

    def analyze_legal_document(self, document_text):
        """
        Analyze a legal document for potential issues and important points
        
        Args:
            document_text (str): The text content of the legal document
            
        Returns:
            dict: Analysis results including loopholes, important points, and recommendations
        """
        analysis_questions = [
            "What are the main terms and conditions in this document?",
            "Are there any potential loopholes or ambiguous clauses in this document?",
            "What are the key rights and obligations of each party?",
            "Are there any missing important clauses or terms that should be included?",
            "What are the payment terms and conditions, and are they clearly defined?",
            "What are the termination conditions and notice periods?",
            "Are there any compliance issues or potential legal concerns?"
        ]
        
        analysis_results = {}
        for question in analysis_questions:
            result = self.query(question)
            analysis_results[question] = result["answer"]
        
        return analysis_results

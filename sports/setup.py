from setuptools import setup, find_packages

setup(
    name="sports_rag",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-community>=0.0.20",
        "langchain-core>=0.1.9",
        "langchain-google-genai>=0.0.5",
        "chromadb==0.4.18",
        "google-generativeai>=0.3.2",
        "google-ai-generativelanguage>=0.4.0",
        "python-dotenv==1.0.0",
        "streamlit==1.29.0",
        "python-multipart==0.0.6",
    ],
)

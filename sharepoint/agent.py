import os
import glob
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# OpenAI Imports
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# Google Vertex AI Imports
from langchain_google_vertexai import VertexAIEmbeddings, VertexAI, VectorSearchVectorStore
try:
    from langchain_google_community import VertexAISearchRetriever
except ImportError:
    # Handle cases where community package might be missing or older version
    print("Warning: langchain-google-community not found or VertexAISearchRetriever missing.")
    VertexAISearchRetriever = None

from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

PERSIST_DIRECTORY = "./chroma_db"
DATA_DIRECTORY = "./data/sharepoint_docs"

class SharePointAgent:
    def __init__(self, data_dir=DATA_DIRECTORY, persist_directory=PERSIST_DIRECTORY, use_google=False):
        self.data_dir = data_dir
        self.persist_directory = persist_directory
        self.use_google = use_google or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if self.use_google:
            print("Using Google Vertex AI Stack")
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
            
            # Embeddings
            self.embeddings = VertexAIEmbeddings(model_name="text-embedding-004", project=project_id, location=location)
            # LLM (Gemini)
            self.llm = VertexAI(model_name="gemini-1.5-pro", temperature=0, project=project_id, location=location)
        else:
            print("Using OpenAI Stack")
            self.embeddings = OpenAIEmbeddings()
            self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
            
        self.vectorstore = None
        self.retriever = None

    def load_documents(self) -> List:
        """Loads documents from the data directory."""
        documents = []
        if not os.path.exists(self.data_dir):
            print(f"Data directory {self.data_dir} does not exist.")
            return []

        loaders = {
            ".pdf": PyPDFLoader,
            ".docx": Docx2txtLoader,
            ".txt": TextLoader,
            ".md": TextLoader
        }

        files = glob.glob(os.path.join(self.data_dir, "**/*.*"), recursive=True)
        print(f"Loading {len(files)} files...")
        
        for file_path in files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in loaders:
                try:
                    loader = loaders[ext](file_path)
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        return documents

    def create_vector_store(self, use_cloud_vector_search=False):
        """Creates or loads the vector store."""
        
        # Option 1: Vertex AI Search (Fully Managed Agent Data Store)
        # This bypasses local vector stores entirely.
        data_store_id = os.getenv("VERTEX_AI_DATA_STORE_ID")
        if self.use_google and data_store_id:
            print(f"Connecting to Vertex AI Search Data Store: {data_store_id}")
            if VertexAISearchRetriever:
                 self.retriever = VertexAISearchRetriever(
                    project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
                    location_id=os.getenv("GOOGLE_CLOUD_LOCATION", "global"), # Search is often global or multi-region
                    data_store_id=data_store_id,
                    max_documents=5,
                    engine_data_type=0 # 0 for Unstructured, 1 for Structured, 2 for Website
                )
                 return
            else:
                 print("VertexAISearchRetriever not available, falling back to local vector store.")

        # Option 2: Local Vector Store (Chroma) with Google Embeddings
        # Or Option 3: Vertex AI Vector Search (Matching Engine) - omitted for simplicity as it requires complex setup
        
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            print("Loading existing vector store...")
            self.vectorstore = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
        else:
            print("Creating new vector store...")
            documents = self.load_documents()
            if not documents:
                print("No documents found to index.")
                # If no docs locally, maybe we rely purely on cloud search?
                if not self.retriever:
                     return

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(documents)
            
            # Using ChromaDB as a local vector store
            self.vectorstore = Chroma.from_documents(
                documents=splits, 
                embedding=self.embeddings, 
                persist_directory=self.persist_directory
            )

        if self.vectorstore:
            self.retriever = self.vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 5})

    def query_agent(self, question: str):
        """Queries the agent."""
        if not self.retriever:
            self.create_vector_store()

        if not self.retriever: 
           return "Agent is empty. Please load documents or configure connection."

        # RAG prompt
        template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
        prompt = ChatPromptTemplate.from_template(template)

        chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        return chain.invoke(question)

if __name__ == "__main__":
    # Check if Google switch is requested (e.g. env var or arg)
    use_google = os.getenv("USE_GOOGLE_AGENT", "False").lower() == "true"
    agent = SharePointAgent(use_google=use_google)
    
    agent.create_vector_store() 
    
    # Interactive loop
    while True:
        try:
            user_input = input("Ask (or 'q' to quit): ")
            if user_input.lower() in ('q', 'quit', 'exit'):
                break
            response = agent.query_agent(user_input)
            print(f"Agent: {response}\n")
        except KeyboardInterrupt:
            break

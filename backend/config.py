import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_cohere import CohereEmbeddings
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# Search for .env in current file's directory (backend/.env) and current working directory
_backend_env = Path(__file__).resolve().parent / ".env"
if _backend_env.exists():
    load_dotenv(dotenv_path=_backend_env)
load_dotenv()


class Config:

    def __init__(
        self,
        persist_directory=None,
        collection_name="deployment_collection"
    ):

        self.persist_directory = persist_directory or str(Path(__file__).resolve().parent / "Chroma_db")
        self.collection_name = collection_name

        self.cohere_api_key = os.getenv("COHERE_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")

        self.embeddings = CohereEmbeddings(# type: ignore[call-arg] 
        model="embed-v4.0",cohere_api_key=self.cohere_api_key)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        self.vector_db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=self.collection_name
        )

        self.llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            groq_api_key=self.groq_api_key,
            temperature=0
        )
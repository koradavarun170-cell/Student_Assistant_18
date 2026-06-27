import os
from dotenv import load_dotenv
from langchain_cohere import CohereEmbeddings
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()


class Config:

    def __init__(
        self,
        persist_directory="./Chroma_db",
        collection_name="deployment_collection"
    ):

        self.persist_directory = persist_directory
        self.collection_name = collection_name

        self.cohere_api_key = os.getenv("COHERE_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")

        self.embeddings = CohereEmbeddings(
            model="embed-v4.0",
            cohere_api_key=self.cohere_api_key
        )

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
            model="llama-3.3-70b-versatile",
            groq_api_key=self.groq_api_key,
            temperature=0
        )
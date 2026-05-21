import os
from langchain_chroma import Chroma

PERSIST_DIR = "./chroma_db"

def create_vector_db(chunks, embeddings):

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )

    return db
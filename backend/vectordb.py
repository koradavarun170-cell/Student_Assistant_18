import os
from langchain_chroma import Chroma

PERSIST_DIR = "./chroma_db"

def create_vector_db(chunks, embeddings):
    
    os.makedirs(PERSIST_DIR, exist_ok=True)

    db = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )

    if chunks:
        db.add_documents(chunks)

    return db
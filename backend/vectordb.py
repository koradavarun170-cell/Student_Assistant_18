import os
from langchain_chroma import Chroma

PERSIST_DIR = "./chroma_db"

def create_vector_db(chunks, embeddings):
    # Ensure the directory exists
    os.makedirs(PERSIST_DIR, exist_ok=True)

    db = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )

    if chunks:
        db.add_documents(chunks)
        # REMOVED: db.persist() is deprecated and auto-saves now!

    return db
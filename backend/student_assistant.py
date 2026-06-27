from uuid import uuid4

from config import Config
from doc_processing import DocumentProcessor
from retriever import RetrieverManager
from rag_chain import RAGChain


class StudentAssistantRAG:

    def __init__(
        self,
        persist_directory="./Chroma_db",
        collection_name="merged_collection"
    ):

        config = Config(persist_directory,collection_name)
        self.vector_db = config.vector_db
        self.processor = DocumentProcessor(config.text_splitter)
        self.retrievers = RetrieverManager(config.vector_db,config.cohere_api_key)
        self.chain = RAGChain(config.llm)

    def add_new_documents(self, dir_path, user_id):

        new_chunks = self.processor.process_directory(dir_path,user_id)

        if not new_chunks:
            return

        ids = [str(uuid4()) for _ in new_chunks]
        self.vector_db.add_documents(documents=new_chunks,ids=ids)
        self.retrievers.refresh(user_id)
    
    def add_file(self, file_paths, user_id):
        new_chunks = self.processor.add_file(file_paths, user_id)
        if not new_chunks:
            return
        ids = [str(uuid4()) for _ in new_chunks]
        self.vector_db.add_documents(documents=new_chunks, ids=ids)
        self.retrievers.refresh(user_id)
        
    def delete_user_documents(self,user_id,filename=None):

        if filename:

            self.vector_db.delete(
                where={
                    "$and": [
                        {"user_id": user_id},
                        {"source_file": filename}
                    ]
                }
            )

        else:

            self.vector_db.delete(
                where={
                    "user_id": user_id
                }
            )

        self.retrievers.refresh(user_id)

    def query(self,question,user_id):

        retriever = self.retrievers.get(user_id)

        if not retriever:

            self.retrievers.refresh(user_id)
            retriever = self.retrievers.get(user_id)

            if not retriever:
                raise ValueError(
                    "No documents uploaded for this user yet."
                )

        docs = retriever.invoke(question)
        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        answer = self.chain.invoke(context,question)

        return {
            "answer": answer,
            "sources": docs
        }
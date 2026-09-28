from uuid import uuid4
from typing import List
from pydantic import BaseModel, Field

from langchain_core.documents import Document
from langgraph.graph import StateGraph, START, END

# pyrefly: ignore [missing-import]
from config import Config
from doc_processing import DocumentProcessor
from retriever import RetrieverManager
# pyrefly: ignore [missing-import]
from rag_chain import RAGChain


class StudentAssistantState(BaseModel):
    question: str = ""
    user_id: str = ""
    documents: List[Document] = Field(default_factory=list)
    context: str = ""
    answer: str = ""


class StudentAssistantRAG:

    def __init__(
        self,
        persist_directory=None,
        collection_name="merged_collection"
    ):
        config = Config(persist_directory, collection_name)
        self.vector_db = config.vector_db
        self.processor = DocumentProcessor(config.text_splitter)
        self.retrievers = RetrieverManager(config.vector_db, config.cohere_api_key)
        self.chain = RAGChain(config.llm)
        self.rag_graph = self._build_rag_graph()

    def _build_rag_graph(self):
        """Constructs an end-to-end RAG StateGraph using LangGraph."""
        workflow = StateGraph(StudentAssistantState)

        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate", self._generate_node)

        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()

    def _retrieve_node(self, state: StudentAssistantState) -> dict:
        """Retrieves relevant chunks using the user's ensemble & rerank retriever."""
        user_id = state.user_id
        question = state.question

        retriever = self.retrievers.get(user_id)
        if not retriever:
            self.retrievers.refresh(user_id)
            retriever = self.retrievers.get(user_id)

            if not retriever:
                raise ValueError("No documents uploaded for this user yet.")

        docs = retriever.invoke(question)
        context = "\n\n".join(doc.page_content for doc in docs)

        return {
            "documents": docs,
            "context": context
        }

    def _generate_node(self, state: StudentAssistantState) -> dict:
        """Generates the grounded response from retrieved context."""
        context = state.context
        question = state.question
        answer = self.chain.invoke(context, question)
        return {"answer": answer}

    def add_new_documents(self, dir_path, user_id):
        new_chunks = self.processor.process_directory(dir_path, user_id)
        if not new_chunks:
            return

        ids = [str(uuid4()) for _ in new_chunks]
        self.vector_db.add_documents(documents=new_chunks, ids=ids)
        self.retrievers.refresh(user_id)

    def add_file(self, file_paths, user_id):
        new_chunks = self.processor.add_file(file_paths, user_id)
        if not new_chunks:
            return
        ids = [str(uuid4()) for _ in new_chunks]
        self.vector_db.add_documents(documents=new_chunks, ids=ids)
        self.retrievers.refresh(user_id)

    def delete_user_documents(self, user_id, filename=None):
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

    def query(self, question, user_id):
        initial_state = StudentAssistantState(
            question=question,
            user_id=user_id,
            documents=[],
            context="",
            answer=""
        )
        result = self.rag_graph.invoke(initial_state)

        return {
            "answer": result["answer"],
            "sources": result["documents"]
        }
from langchain_core.documents import Document
from langchain_classic.retrievers import (
    EnsembleRetriever,
    ContextualCompressionRetriever
)
from langchain_community.retrievers import BM25Retriever
from langchain_cohere import CohereRerank


class RetrieverManager:

    def __init__(self, vector_db, cohere_key):

        self.vector_db = vector_db
        self.cohere_key = cohere_key

        self.user_retrievers = {}

    def refresh(self, user_id):

        search_results = self.vector_db.get(
            where={"user_id": user_id},
            include=["documents", "metadatas"]
        )

        user_specific_chunks = []

        if (
            search_results
            and "documents" in search_results
            and search_results["documents"]
        ):

            user_specific_chunks = [

                Document(
                    page_content=text,
                    metadata=meta or {}
                )

                for text, meta in zip(
                    search_results["documents"],
                    search_results["metadatas"]
                )

            ]

        if not user_specific_chunks:

            self.user_retrievers[user_id] = None
            return

        chroma = self.vector_db.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 5,
                "filter": {
                    "user_id": user_id
                }
            }
        )

        bm25 = BM25Retriever.from_documents(user_specific_chunks)
        bm25.k = 5

        ensemble = EnsembleRetriever(
            retrievers=[chroma, bm25],
            weights=[0.6, 0.4]
        )

        compressor = CohereRerank(
            model="rerank-english-v3.0",
            cohere_api_key=self.cohere_key,
            top_n=3
        )

        self.user_retrievers[user_id] = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=ensemble
        )

    def get(self, user_id):

        return self.user_retrievers.get(user_id)
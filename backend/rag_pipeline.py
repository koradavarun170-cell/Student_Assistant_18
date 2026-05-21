from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def get_splitter():

    return RecursiveCharacterTextSplitter(
        chunk_size=1000,       
        chunk_overlap=200,     
        separators=["\n\n", "\n", ".", " ", ""]
    )


def get_chunks(documents):

    splitter = get_splitter()
    chunks = []

    for doc in documents:

        split_docs = splitter.split_documents([doc])

        for i, chunk in enumerate(split_docs):

            chunks.append(Document(
                page_content=chunk.page_content,
                metadata={
                    **doc.metadata,
                    "chunk_id": i
                }
            ))

    return chunks
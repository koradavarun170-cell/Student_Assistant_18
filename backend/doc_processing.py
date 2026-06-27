import os

from langchain_community.document_loaders import (
    PDFMinerLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader
)
from langchain_community.document_loaders.parsers import RapidOCRBlobParser


class DocumentProcessor:

    def __init__(self, splitter):
        self.text_splitter = splitter
    def check_file(self,file_lower,full_path,file,user_id):
        if file_lower.endswith(".pdf"):

            loader = PDFMinerLoader(
                full_path,
                extract_images=True,
                mode="page",
                images_parser=RapidOCRBlobParser(),
                images_inner_format="html-img"
            )

            docs = loader.load()

        elif file_lower.endswith((".docx", ".doc")):

            loader = Docx2txtLoader(full_path)
            docs = loader.load()

        elif file_lower.endswith((".pptx", ".ppt")):

            loader = UnstructuredPowerPointLoader(
                full_path,
                mode="elements"
            )

            docs = loader.load()

        if docs:

            chunks = self.text_splitter.split_documents(docs)
            for chunk in chunks:
                chunk.metadata["user_id"] = user_id
                chunk.metadata["source_file"] = file

            return chunks
        return []
        
    def process_directory(self, dir_path, user_id):

        split_chunks = []

        if not os.path.isdir(dir_path):
            raise ValueError(f"Provided path is not a directory: {dir_path}")

        for file in os.listdir(dir_path):

            full_path = os.path.join(dir_path, file)
            file_lower = file.lower()
            chunks=self.check_file(file_lower,full_path,file,user_id)
            split_chunks.extend(chunks)
        return split_chunks
        
    def add_file(self, file_paths, user_id):

        split_chunks = []
        for full_path in file_paths:

            file = os.path.basename(full_path)
            file_lower = file.lower()
            chunks = self.check_file(file_lower,full_path,file,user_id)
            split_chunks.extend(chunks)

        return split_chunks

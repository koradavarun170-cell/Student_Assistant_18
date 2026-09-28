import os
import shutil
from pathlib import Path
from typing import List, Annotated
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from student_assistant import StudentAssistantRAG
from models.request_models import QueryRequest, DeleteRequest

app = FastAPI(title="Student Assistant RAG",version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
rag = StudentAssistantRAG()

UPLOAD_FOLDER = str(Path(__file__).resolve().parent / "source_files")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
async def home():
    return {"status": "Running"}

@app.post("/upload")
async def upload_documents(
    user_id: Annotated[str, Form()],
    files: List[UploadFile] = File(...,media_type="multipart/form-data")
):
    user_folder = os.path.join(UPLOAD_FOLDER, user_id)
    first_upload = not os.path.exists(user_folder)

    os.makedirs(user_folder, exist_ok=True)

    uploaded_paths = []

    for file in files:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")
        path = os.path.join(user_folder, file.filename)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_paths.append(path)

    if first_upload:
        rag.add_new_documents(user_folder, user_id)
    else:
        rag.add_file(uploaded_paths, user_id)

    return {"message": "Documents uploaded successfully."}

@app.post("/query")
async def query(request: QueryRequest):
    try:
        result = rag.query(request.question, request.user_id)
        seen = set()
        sources = []
        for doc in result["sources"]:
            file = doc.metadata.get("source_file")
            page = doc.metadata.get("page", "N/A")
            key = (file, page)
            if key not in seen:
                seen.add(key)
                sources.append({"file": file, "page": page})
        return {"answer": result["answer"], "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.delete("/delete")
async def delete(request: DeleteRequest):

    rag.delete_user_documents(
        request.user_id,
        request.filename
    )

    return {
        "message": "Deleted successfully."
    }
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FOLDER = "./data"
os.makedirs(DATA_FOLDER, exist_ok=True)

embeddings = None
llm = None
db = None


def init_models():
    global embeddings, llm

    from backend.embeddings import get_embeddings
    from backend.model import get_llm

    if embeddings is None:
        embeddings = get_embeddings()

    if llm is None:
        llm = get_llm()

@app.get("/")
def health_check():
    print("Health check endpoint called")
    return {
        "status": "healthy",
        "message": "FastAPI backend online!"
    }

@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    global db

    from backend.code_loader import load_code
    from backend.rag_pipeline import get_chunks
    from backend.vectordb import create_vector_db

    try:
        init_models()

        path = os.path.join(DATA_FOLDER, file.filename)

        with open(path, "wb") as f:
            f.write(await file.read())

        docs = load_code(DATA_FOLDER)

        chunks = get_chunks(docs)

        db = create_vector_db(chunks, embeddings)

        return {
            "message": f"{file.filename} uploaded successfully!"
        }

    except Exception as e:
        return {"error": str(e)}

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query(data: QueryRequest):

    global db

    from backend.response import get_response

    try:

        if db is None:
            return {
                "error": "No documents uploaded yet."
            }

        init_models()

        answer = get_response(
            data.question,
            db,
            llm
        )

        return {
            "answer": answer
        }

    except Exception as e:
        return {"error": str(e)}
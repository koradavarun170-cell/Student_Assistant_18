# 📚 StudyMind - Document Assistant V2

A production-ready Multi-User Document Assistant built with **FastAPI**, **LangGraph**, and **Streamlit**. It enables students and researchers to upload multi-format documents (PDF, DOCX, PPTX) and query them with contextual retrieval, hybrid search (Chroma + BM25 Ensemble), Cohere Reranking, and grounded answer synthesis powered by LLaMA 3.3 via Groq.

---

## 🏗️ Architecture & Enhancements

- **Graph-Based RAG Orchestration (LangGraph)**: The retrieval and generation pipelines are structured as compiled `StateGraph` workflows (`START -> retrieve -> generate -> END`). LangChain is utilized where optimal (prompt templates, document loaders, Chroma vector store, Cohere reranking, and ChatGroq model integration).
- **Interactive UI (Streamlit)**: Streamlit frontend matching the warm StudyMind design aesthetic with session scoping, multi-file uploads with type badges, document management (single-file deletion), chat history, starter question chips, and citation badges.
- **Decoupled Client-Server Architecture**: The frontend interacts with FastAPI via REST endpoints, allowing independent scaling, testing, and deployment.
- **Multi-Cloud Ready (Render / Docker)**: Pre-configured Dockerfiles, multi-service `docker-compose.yml`, and `render.yaml` blueprint for 1-click Render deployment (replacing AWS dependencies).

---

## 📁 Project Structure

The project structure is strictly preserved:

```text
Student_Assistant_V2/
├── backend/
│   ├── Chroma_db/               # Persistent Chroma vector store
│   ├── models/
│   │   └── request_models.py    # Pydantic schemas (QueryRequest, DeleteRequest)
│   ├── source_files/            # Uploaded document staging by user_id
│   ├── .dockerignore
│   ├── .env.example             # Environment variable template
│   ├── config.py                # Embeddings, VectorDB, & LLM initialization
│   ├── doc_processing.py        # PDF, DOCX, and PPTX OCR/extractors
│   ├── Dockerfile               # Production container for FastAPI backend
│   ├── docker-compose.yml       # Backend-specific docker-compose
│   ├── main.py                  # FastAPI server with CORS & endpoints
│   ├── rag_chain.py             # LangGraph Generation StateGraph
│   ├── requirements.txt         # Backend dependencies
│   ├── retriever.py             # EnsembleRetriever (Chroma + BM25) + Cohere Rerank
│   └── student_assistant.py     # End-to-end LangGraph RAG Agent
├── frontend/
│   ├── app.py                   # Streamlit Frontend application
│   ├── Dockerfile               # Production container for Streamlit frontend
│   ├── requirements.txt         # Frontend dependencies
│   └── src/                     # Preserved original UI assets
├── docker-compose.yml           # Root full-stack orchestration
├── pyproject.toml               # Project dependencies specification
├── render.yaml                  # 1-click deployment blueprint for Render
├── requirements.txt             # Root dependencies
└── README.md                    # Documentation
```

---

## ⚙️ Environment Variables

Create a `.env` file inside the `backend/` directory (or set them in your deployment environment):

```ini
# Cohere API Key (for embeddings and reranking)
COHERE_API_KEY=your_cohere_api_key_here

# Groq API Key (for LLaMA 3.3 LLM)
GROQ_API_KEY=your_groq_api_key_here
```

For the Streamlit frontend, you can optionally configure:

```ini
# Backend API URL (default: http://localhost:8000)
BACKEND_URL=http://localhost:8000
```

---

## 🚀 Running Locally

### 1. Setup Environment
```bash
# Using uv (recommended)
uv venv
uv pip install -r requirements.txt

# Or using standard pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Backend (FastAPI)
```bash
cd backend
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
API docs available at: `http://127.0.0.1:8000/docs`

### 3. Run Frontend (Streamlit)
In a separate terminal:
```bash
cd frontend
uv run streamlit run app.py
```
Streamlit app available at: `http://localhost:8501`

---

## 🐳 Docker Setup

Run both the FastAPI backend and Streamlit frontend together:

```bash
docker compose up --build
```

- **Frontend**: `http://localhost:8501`
- **Backend API**: `http://localhost:8000`

---

## ☁️ Deployment Guide (Render / Streamlit Cloud)

### Option 1: 1-Click Render Blueprint (Recommended)
1. Push your repository to GitHub.
2. Log into [Render](https://render.com).
3. Click **New +** -> **Blueprint**.
4. Select your repository. Render will automatically detect `render.yaml` and provision:
   - **`student-assistant-backend`**: Docker Web Service running FastAPI.
   - **`student-assistant-frontend`**: Docker Web Service running Streamlit.
5. In the Render Dashboard, fill in `COHERE_API_KEY` and `GROQ_API_KEY` under the backend environment variables.

### Option 2: Streamlit Community Cloud (Frontend) + Render (Backend)
- Deploy `backend/` to Render as a Web Service (Docker).
- Deploy `frontend/app.py` to [Streamlit Community Cloud](https://share.streamlit.io/) for free:
  - Repository: Your GitHub repo
  - Main file path: `frontend/app.py`
  - In App Settings > Secrets, add:
    ```toml
    BACKEND_URL = "https://your-render-backend-url.onrender.com"
    ```

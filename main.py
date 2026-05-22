from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
# Enable CORS cleanly for both local development and production domains
CORS(app, resources={r"/*": {"origins": "*"}})

DATA_FOLDER = "./data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# Lazy-loaded globals (CRITICAL for keeping memory under Render's 512MB limit)
embeddings = None
llm = None
db = None


# ------------------ 1. HEALTH CHECK ROUTE ------------------
@app.route("/", methods=["GET"])
def health_check():
    # Keep this completely blank of any imports or logic. 
    # This must remain a lightning-fast return so Render's scanner hooks it instantly.
    return jsonify({
        "status": "healthy", 
        "message": "Render successfully bound to the port!"
    }), 200


# ------------------ INIT MODELS LAZILY ------------------
def init_models():
    global embeddings, llm
    
    # Keeping heavy imports strictly inside functions ensures Gunicorn boots instantly
    from backend.embeddings import get_embeddings
    from backend.model import get_llm

    if embeddings is None:
        embeddings = get_embeddings()

    if llm is None:
        llm = get_llm()


# ------------------ UPLOAD ROUTE ------------------
@app.route("/upload", methods=["POST", "OPTIONS"])
def upload():
    # Handle CORS Preflight browser request cleanly
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    global db
    from backend.code_loader import load_code
    from backend.rag_pipeline import get_chunks
    from backend.vectordb import create_vector_db

    try:
        init_models()

        if "file" not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        path = os.path.join(DATA_FOLDER, file.filename)
        file.save(path)

        docs = load_code(DATA_FOLDER)
        chunks = get_chunks(docs)

        db = create_vector_db(chunks, embeddings)

        return jsonify({
            "message": "File uploaded successfully"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------ QUERY ROUTE ------------------
@app.route("/query", methods=["POST", "OPTIONS"])
def query():
    # Handle CORS Preflight browser request cleanly
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    global db
    from backend.response import get_response

    try:
        if db is None:
            return jsonify({
                "error": "No documents uploaded yet"
            }), 400

        init_models()

        data = request.get_json()
        if not data or "question" not in data:
            return jsonify({"error": "Missing question in request body"}), 400
            
        question = data["question"]
        answer = get_response(question, db, llm)

        return jsonify({
            "answer": answer
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------ ENTRY POINT ------------------
if __name__ == "__main__":
    # This only runs during local development python main.py execution
    print("System initialized safely via local entry point")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
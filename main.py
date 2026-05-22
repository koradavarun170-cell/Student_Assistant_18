from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from backend.code_loader import load_code
from backend.rag_pipeline import get_chunks
from backend.embeddings import get_embeddings
from backend.vectordb import create_vector_db
from backend.model import get_llm
from backend.response import get_response


app = Flask(__name__)
CORS(app)

DATA_FOLDER = "./data"
os.makedirs(DATA_FOLDER, exist_ok=True)
embeddings = get_embeddings()
llm = get_llm()

print("System ready")
db=None

@app.route("/upload", methods=["POST"])
def upload():

    global db

    try:
        file = request.files["file"]
        path = os.path.join(
            DATA_FOLDER,
            file.filename
        )
        file.save(path)
        docs = load_code(DATA_FOLDER)

        chunks = get_chunks(docs)

        db = create_vector_db(
            chunks,
            embeddings
        )

        return jsonify({
            "message": "File uploaded successfully"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/query", methods=["POST"])
def query():

    try:
        global db

        if db is None:
            return jsonify({
                "error": "No documents uploaded yet"
            }), 400

        data = request.get_json()
        question = data["question"]

        print("Question:", question)

        answer = get_response(
            question,
            db,
            llm
        )

        return jsonify({
            "answer": answer
        })

    except Exception as e:
        print("QUERY ERROR:")
        print(str(e))

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
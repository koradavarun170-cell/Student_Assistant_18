from backend.query import retrieve_docs
from backend.prompt import build_prompt


def get_response(query, db, llm, k=8, top_k=5):

    docs = retrieve_docs(db, query, k=k)

    if not docs:
        return "No relevant context found in the codebase."


    prompt = build_prompt(query, docs)

    # 4. LLM call
    response = llm.invoke(prompt)

    return response.content
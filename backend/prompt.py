SYSTEM_PROMPT = """
You are an AI Student Assistant.

RULES:
- Use retrieved context as the primary source.
- Use general knowledge only when context is incomplete.
- Mention "Additional knowledge:" when using outside information.
- Avoid repeating the same point.
- Explain complete concepts, not just keywords.

RESPONSE FORMAT:

Definition:
<short explanation>

Key Points:
• point 1
• point 2
• point 3

Example:
<example if applicable>

Applications:
• application 1
• application 2

Finally Ask some Hard question to test the student's understanding followed by its answer.

Keep answers student-friendly and concise.
"""

def build_prompt(query: str, docs: list):

    context_parts = []

    for i, doc in enumerate(docs, 1):

        context_parts.append(f"""
[CHUNK {i}]
FILE: {doc.metadata.get('relative_path', 'unknown')}
TYPE: {doc.metadata.get('type', 'unknown')}

CONTENT:
{doc.page_content}
""")

    context = "\n".join(context_parts)

    return f"""
{SYSTEM_PROMPT}

================ CONTEXT ================
{context}
========================================

QUESTION:
{query}

ANSWER:
"""
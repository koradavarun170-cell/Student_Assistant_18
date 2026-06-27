from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class RAGChain:

    def __init__(self, llm):

        self.prompt = ChatPromptTemplate.from_template(
            """You are a helpful student assistant. Your job is to help students understand their study material clearly.

            Answer the question thoroughly using only the provided context.
            - Break down complex concepts simply
            - Use examples from the context where possible  
            - If the answer spans multiple topics, structure your response with clear points
            - If the answer is not in the context, say: "I could not find this in your uploaded documents."
            - Do not repeat the same point twice
            Context:
            {context}

            Question:
            {question}

            Answer:"""
            )

        self.chain = self.prompt | llm | StrOutputParser()

    def invoke(self, context, question):

        return self.chain.invoke(
            {
                "context": context,
                "question": question
            }
        )
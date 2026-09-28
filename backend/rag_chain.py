from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END


class RAGGenerationState(BaseModel):
    context: str = ""
    question: str = ""
    answer: str = ""


class RAGChain:
    """
    RAG Generation pipeline powered by LangGraph StateGraph.
    Integrates LangChain prompt templates, LLMs, and output parsers inside the graph node.
    """

    def __init__(self, llm):
        self.llm = llm
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
        self.output_parser = StrOutputParser()
        self.graph = self._build_graph()

    def _generate_node(self, state: RAGGenerationState) -> dict:
        """LangGraph node: Formats prompt with context & question, calls LLM, and parses output."""
        generation_chain = self.prompt | self.llm | self.output_parser
        answer = generation_chain.invoke(
            {
                "context": state.context,
                "question": state.question
            }
        )
        return {"answer": answer}

    def _build_graph(self):
        """Constructs and compiles the LangGraph StateGraph."""
        workflow = StateGraph(RAGGenerationState)
        workflow.add_node("generate", self._generate_node)
        workflow.add_edge(START, "generate")
        workflow.add_edge("generate", END)
        return workflow.compile()

    def invoke(self, context: str, question: str) -> str:
        """Executes the LangGraph generation pipeline."""
        initial_state = RAGGenerationState(
            context=context,
            question=question,
            answer=""
        )
        result = self.graph.invoke(initial_state)
        return result["answer"]
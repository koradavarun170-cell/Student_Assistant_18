from pydantic import BaseModel


class QueryRequest(BaseModel):
    user_id: str
    question: str


class DeleteRequest(BaseModel):
    user_id: str
    filename: str | None = None
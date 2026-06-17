from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from agent_router import answer_message


app = FastAPI(title="Ecommerce RAG Agent")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    platform: str = "etsy"


class ChatResponse(BaseModel):
    intent: str
    answer: str
    tool_result: Optional[dict] = None
    sources: list[dict] = Field(default_factory=list)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> dict:
    return answer_message(request.message, platform=request.platform)

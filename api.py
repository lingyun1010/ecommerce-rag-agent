from typing import Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from agent_router import answer_message
from rag_service import clear_query_engine_cache
from store_knowledge import StoreKnowledgeError, generate_store_knowledge, save_knowledge_files


app = FastAPI(title="Ecommerce RAG Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ARTIFACT_DIR = Path("generated_knowledge")
RAG_RUNTIME_DIR = Path("runtime_knowledge/current")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    platform: str = "etsy"


class ChatResponse(BaseModel):
    intent: str
    answer: str
    tool_result: Optional[dict] = None
    sources: list[dict] = Field(default_factory=list)


class StoreKnowledgeRequest(BaseModel):
    store_url: str = Field(..., min_length=1)
    output_format: str = "markdown"


class StoreKnowledgeResponse(BaseModel):
    store_url: str
    output_format: str
    product_count: int
    files: dict[str, str]
    markdown: str
    download_url: str
    warning: str = ""
    chat_enabled: bool = True


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> dict:
    return answer_message(request.message, platform=request.platform)


@app.post("/knowledge/generate", response_model=StoreKnowledgeResponse)
def generate_knowledge(request: StoreKnowledgeRequest) -> dict:
    try:
        result = generate_store_knowledge(
            store_url=request.store_url,
            output_format=request.output_format,
        )
    except StoreKnowledgeError as exc:
        raise HTTPException(status_code=400, detail=exc.as_dict()) from exc

    artifact = save_knowledge_files(
        files=result["files"],
        store_url=result["store_url"],
        output_dir=ARTIFACT_DIR,
    )

    RAG_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    for filename, content in result["files"].items():
        (RAG_RUNTIME_DIR / filename).write_text(content, encoding="utf-8")

    clear_query_engine_cache()

    return {
        **result,
        "download_url": f"/knowledge/download/{artifact['artifact_id']}",
        "chat_enabled": True,
    }


@app.get("/knowledge/download/{artifact_id}")
def download_knowledge(artifact_id: str):
    path = ARTIFACT_DIR / f"{artifact_id}.zip"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Knowledge artifact not found.")

    return FileResponse(
        path,
        media_type="application/zip",
        filename=f"{artifact_id}.zip",
    )

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data", exist_ok=True)

from src.agents.orchestrator import chat

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    user_id: str = "user"

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    response = chat(req.message, req.session_id, req.user_id)
    response_type = (
        "clarification"
        if "?" in response and len(response) < 300
        else "answer"
    )
    return {
        "response": response,
        "response_type": response_type
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
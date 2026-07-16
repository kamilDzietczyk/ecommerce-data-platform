from fastapi import FastAPI
from pydantic import BaseModel

from ai_assistant.app.assistant import answer_question


app = FastAPI(
    title="Ecommerce AI Analytics Assistant",
    description="Experimental AI analytics assistant for ecommerce marts data.",
    version="0.1.0",
)


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ai-assistant",
    }


@app.post("/ask")
def ask_question(request: AskRequest):
    return answer_question(request.question)
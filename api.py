from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from agent import app as agent_app, message_text
from config import MODEL_NAME

api = FastAPI(title="FinDoc AI")


class AskRequest(BaseModel):
    question: str
    conversation_id: str = "default"


class AskResponse(BaseModel):
    answer: str
    tools_used: list[str]


@api.get("/health")
def health():
    return {"status": "ok"}


@api.get("/info")
def info():
    return {"name": "FinDoc AI", "model": MODEL_NAME}


@api.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    chat = {"configurable": {"thread_id": request.conversation_id}}
    try:
        result = agent_app.invoke({"messages": [HumanMessage(content=request.question)]}, chat)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"AI service unavailable ({type(error).__name__}), please try again")

    tools_used = []
    for message in reversed(result["messages"]):
        if isinstance(message, HumanMessage):
            break
        for call in getattr(message, "tool_calls", []):
            tools_used.append(call["name"])

    return AskResponse(answer=message_text(result["messages"][-1]), tools_used=tools_used)
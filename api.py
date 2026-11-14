import psycopg
from fastapi import UploadFile

from invoice_pipeline import extract_invoice, check_invoice, save_invoice
from invoice_schema import Invoice
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

class InvoiceResponse(BaseModel):
    status: str
    invoice_id: int | None
    invoice: Invoice
    problems: list[str]


ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp"}

@api.post("/invoices", response_model=InvoiceResponse)
def upload_invoice(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Please upload a PNG, JPEG or WebP image")

    image_bytes = file.file.read()

    try:
        invoice = extract_invoice(image_bytes, file.content_type)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Could not read the invoice ({type(error).__name__})")

    problems = check_invoice(invoice)

    try:
        invoice_id = save_invoice(invoice)
        status = "saved"
    except psycopg.errors.UniqueViolation:
        invoice_id = None
        status = "duplicate"

    return InvoiceResponse(status=status, invoice_id=invoice_id, invoice=invoice, problems=problems)
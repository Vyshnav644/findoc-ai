from typing import Literal

from google.genai import types
from pydantic import BaseModel, Field

from config import MODEL_NAME
from llm import client


class Route(BaseModel):
    destination: Literal["invoices", "vat_rules", "other"] = Field(
        description=(
            "invoices: questions about the company's own invoices, suppliers, amounts, dates or VAT paid. "
            "vat_rules: questions about UAE VAT law and rules, such as registration, tax invoices or what VAT can be recovered. "
            "other: anything else."
        )
    )
def route_question(question):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=f"Classify this question for a UAE invoice and VAT assistant:\n{question}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Route,
        ),
    )
    route = response.parsed
    if route is None:
        return "other"
    return route.destination

if __name__ == "__main__":
    questions = [
        "How much VAT did we pay in March 2026?",
        "Can I claim back VAT on a gift for my employee?",
        "Which supplier did we pay the most?",
        "When do I have to register for VAT?",
        "What is the weather in Dubai today?",
    ]
    for q in questions:
        print(route_question(q), "<-", q)    
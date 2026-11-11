from router import route_question
from rag import answer_from_guide, GUIDE_NAME
import re
import psycopg
from google.genai import types, errors
from pydantic import BaseModel, Field

from config import MODEL_NAME, DATABASE_URL
from llm import client

with open("sql/schema.sql") as f:
    schema = f.read()


class SqlQuery(BaseModel):
    sql: str | None = Field(
        default=None,
        description="One PostgreSQL SELECT query on the invoices table, or null if you cannot write one",
    )
    message: str | None = Field(
        default=None,
        description="Only if sql is null: a short message for the user, either a clarifying question or why the invoice data cannot answer",
    )


def is_safe_sql(sql):
    cleaned = sql.strip().rstrip(";").lower()
    if not cleaned.startswith("select"):
        return False
    if ";" in cleaned:
        return False
    for word in ["insert", "update", "delete", "drop", "alter", "create", "truncate", "grant"]:
        if re.search(rf"\b{word}\b", cleaned):
            return False
    return True


while True:
    question = input("Ask a question (or type exit): ")
    if question.lower() == "exit":
        break

    try:
        destination = route_question(question)
    except errors.ServerError:
        print("Gemini is busy right now, please try again.")
        print()
        continue

    if destination == "other":
        print("FinDoc: I can answer questions about your invoices or about UAE VAT rules.")
        print()
        continue

    if destination == "vat_rules":
        try:
            answer, results = answer_from_guide(question)
        except errors.ServerError:
            print("Gemini is busy right now, please try again.")
            print()
            continue
        print("Answer:", answer)
        print("Searched:", ", ".join(chunk["section"] for score, chunk in results))
        print(f"Source: {GUIDE_NAME}. Rules may have changed since this guide was issued.")
        print()
        continue

    prompt = f"""You write PostgreSQL queries for an invoice database.

Database schema:
{schema}

Rules:
- Only answer from the invoices table. Never write facts or answers as text inside the SQL.
- If the question is not about the invoice data (for example VAT laws or rules), set sql to null and explain in message that the invoice database cannot answer it.
- If the question mentions a month or period but no year, set sql to null and ask which year in message.

Write one SELECT query that answers this question:
{question}"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SqlQuery,
            ),
        )
    except errors.ServerError:
        print("Gemini is busy right now, please try again.")
        print()
        continue

    result = response.parsed
    if result is None:
        print("Gemini did not return a query. Try rephrasing.")
        continue

    if result.sql is None:
        print("FinDoc:", result.message)
        print()
        continue

    print("SQL:", result.sql)

    if not is_safe_sql(result.sql):
        print("Blocked: that question would need a query that changes data.")
        continue

    with psycopg.connect(DATABASE_URL) as conn:
        conn.read_only = True
        rows = conn.execute(result.sql).fetchall()

    print("Result:", rows)

    answer_prompt = f"""Question: {question}
Database result rows: {rows}

Answer the question in one short sentence for an accountant.
Use the exact numbers from the result. Amounts are in AED."""

    try:
        answer = client.models.generate_content(
            model=MODEL_NAME,
            contents=answer_prompt,
        )
    except errors.ServerError:
        print("Gemini is busy right now, please try again.")
        print()
        continue
    print("Answer:", answer.text)
    print()
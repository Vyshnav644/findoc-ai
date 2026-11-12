import re

import psycopg
from google.genai import types
from pydantic import BaseModel, Field

from config import MODEL_NAME, DATABASE_URL
from llm import client

with open("sql/schema.sql") as f:
    SCHEMA = f.read()


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

def query_invoices(question):
    prompt = f"""You write PostgreSQL queries for an invoice database.

Database schema:
{SCHEMA}

Rules:
- Only answer from the invoices table. Never write facts or answers as text inside the SQL.
- If the question is not about the invoice data (for example VAT laws or rules), set sql to null and explain in message that the invoice database cannot answer it.
- If the question mentions a month or period but no year, set sql to null and ask which year in message.

Write one SELECT query that answers this question:
{question}"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SqlQuery,
        ),
    )

    result = response.parsed
    if result is None:
        return {"message": "Could not turn that into a query. Try rephrasing."}
    if result.sql is None:
        return {"message": result.message}
    if not is_safe_sql(result.sql):
        return {"message": "Blocked: that question would need a query that changes data."}

    with psycopg.connect(DATABASE_URL) as conn:
        conn.read_only = True
        rows = conn.execute(result.sql).fetchall()

    return {"sql": result.sql, "rows": rows}

if __name__ == "__main__":
    print(query_invoices("How much VAT did we pay in March 2026?"))
    print(query_invoices("How much VAT did we pay in March?"))
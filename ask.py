import re
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
client = genai.Client(
    http_options=types.HttpOptions(
        timeout=30_000,
        retry_options=types.HttpRetryOptions(attempts=1),
    )
)

with open("sql/schema.sql") as f:
    schema = f.read()


class SqlQuery(BaseModel):
    sql: str = Field(description="One PostgreSQL SELECT query that answers the question")

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

question = "How much VAT did we pay in March 2026?"

prompt = f"""You write PostgreSQL queries for an invoice database.

Database schema:
{schema}

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
    raise ValueError("Gemini did not return a query")

print("Question:", question)
print("SQL:", result.sql)

print("Gemini's query:", is_safe_sql(result.sql))
print("DROP TABLE:", is_safe_sql("DROP TABLE invoices"))
print("Hidden DELETE:", is_safe_sql("SELECT * FROM invoices; DELETE FROM invoices"))
print("created_at:", is_safe_sql("SELECT created_at FROM invoices"))
print("Update Traders:", is_safe_sql("SELECT * FROM invoices WHERE vendor_name = 'Update Traders'"))
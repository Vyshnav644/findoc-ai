import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is missing from .env")

with psycopg.connect(DATABASE_URL) as conn:
    row = conn.execute(
        "SELECT SUM(vat_amount) FROM invoices "
        "WHERE invoice_date BETWEEN '2026-03-01' AND '2026-03-31'"
    ).fetchone()

print("March VAT:", row[0])
print(type(row[0]))
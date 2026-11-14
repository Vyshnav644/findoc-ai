import psycopg
from google.genai import types

from config import MODEL_NAME, DATABASE_URL
from invoice_schema import Invoice
from llm import client


def extract_invoice(image_bytes, mime_type):
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[image_part, "Extract the invoice details from this image."],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Invoice,
        ),
    )
    invoice = response.parsed
    if invoice is None:
        raise ValueError("Gemini's reply did not match the Invoice form")
    return invoice

def check_invoice(invoice):
    problems = []

    difference = abs(invoice.subtotal + invoice.vat_amount - invoice.total)
    if difference >= 0.01:
        problems.append(f"Subtotal + VAT does not match total (off by {difference:.2f})")

    expected_vat = invoice.subtotal * 0.05
    if abs(invoice.vat_amount - expected_vat) >= 0.01:
        problems.append(f"VAT is not 5% of subtotal (expected {expected_vat:.2f})")

    return problems

def save_invoice(invoice):
    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute(
            "INSERT INTO invoices "
            "(vendor_name, invoice_number, invoice_date, subtotal, vat_amount, total) "
            "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (
                invoice.vendor_name,
                invoice.invoice_number,
                invoice.invoice_date,
                invoice.subtotal,
                invoice.vat_amount,
                invoice.total,
            ),
        ).fetchone()
    return row[0]
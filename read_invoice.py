import psycopg
from google.genai import types
from invoice_schema import Invoice

from config import MODEL_NAME, DATABASE_URL
from llm import client

print("Using model:", MODEL_NAME)

# ----- 1. Load the invoice image -----

with open("samples/sample_invoice_01.png", "rb") as f:
    image_bytes = f.read()

print("Image loaded, size in bytes:", len(image_bytes))

image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")

# ----- 2. Ask Gemini to fill in the Invoice form -----

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
print(invoice)

# ----- 3. Consistency checks (work on any invoice) -----

difference = abs(invoice.subtotal + invoice.vat_amount - invoice.total)
if difference < 0.01:
    print("PASS: subtotal + VAT matches total")
else:
    print("FAIL: subtotal + VAT does not match total, off by", difference)

expected_vat = invoice.subtotal * 0.05
vat_difference = abs(invoice.vat_amount - expected_vat)
if vat_difference < 0.01:
    print("PASS: VAT is 5% of subtotal")
else:
    print("FAIL: VAT is not 5% of subtotal, off by", vat_difference)

# ----- 4. Accuracy against known answers (sample invoice only) -----

expected = Invoice(
    vendor_name="Example Supplies LLC",
    invoice_number="INV-2026-0147",
    invoice_date="2026-03-15",
    subtotal=2535.00,
    vat_amount=126.75,
    total=2661.75,
)

correct = 0
for field in Invoice.model_fields:
    got = getattr(invoice, field)
    want = getattr(expected, field)
    if isinstance(got, str):
        got = got.lower().strip()
        want = want.lower().strip()
    if got == want:
        correct = correct + 1
        print("PASS:", field)
    else:
        print("FAIL:", field, "| got", got, "| expected", want)

print("Accuracy:", correct, "out of", len(Invoice.model_fields))

# ----- 5. Save to PostgreSQL (skip if already saved) -----

try:
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
    print("Saved to database with id:", row[0])
except psycopg.errors.UniqueViolation:
    print("Already saved: this invoice is in the database, skipped.")
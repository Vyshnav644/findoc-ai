import psycopg

from config import MODEL_NAME
from invoice_pipeline import extract_invoice, check_invoice, save_invoice
from invoice_schema import Invoice

print("Using model:", MODEL_NAME)

with open("samples/sample_invoice_01.png", "rb") as f:
    image_bytes = f.read()

invoice = extract_invoice(image_bytes, "image/png")
print(invoice)

problems = check_invoice(invoice)
if problems:
    for problem in problems:
        print("FAIL:", problem)
else:
    print("PASS: all checks")

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
    else:
        print("FAIL:", field, "| got", got, "| expected", want)
print("Accuracy:", correct, "out of", len(Invoice.model_fields))

try:
    print("Saved to database with id:", save_invoice(invoice))
except psycopg.errors.UniqueViolation:
    print("Already saved: this invoice is in the database, skipped.")
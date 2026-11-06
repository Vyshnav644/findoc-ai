from pydantic import BaseModel

class Invoice(BaseModel):
    vendor_name: str
    invoice_number: str
    invoice_date: str
    subtotal: float
    vat_amount: float
    total: float

example = Invoice(
    vendor_name="Example Supplies LLC",
    invoice_number="INV-2026-0147",
    invoice_date="2026-03-15",
    subtotal=2535.00,
    vat_amount=126.75,
    total=2661.75,
)
print(example)
print(example.total + 1)    
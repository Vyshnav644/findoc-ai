from datetime import date
from pydantic import BaseModel, Field

class Invoice(BaseModel):
    vendor_name: str = Field(description="Name of the company that issued the invoice")
    invoice_number: str = Field(description="Invoice number exactly as printed")
    invoice_date: date = Field(description="Invoice issue date in YYYY-MM-DD format")
    subtotal: float = Field(description="Amount before VAT, as a plain number")
    vat_amount: float = Field(description="VAT amount charged, as a plain number")
    total: float = Field(description="Final amount including VAT, as a plain number")
if __name__ == "__main__":
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
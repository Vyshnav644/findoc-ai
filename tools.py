from langchain_core.tools import tool

from invoice_sql import query_invoices
from retrieve import search


@tool
def invoice_database(question: str) -> str:
    """Answer questions about the company's own invoices stored in the database:
    suppliers, invoice numbers, dates, subtotals, VAT paid and totals.
    Pass the question in plain English, including the year if the user gave one."""
    result = query_invoices(question)
    return str(result)

@tool
def vat_guide(question: str) -> str:
    """Search the official FTA Taxable Person Guide (VATG001, June 2018) for UAE VAT rules:
    registration, tax invoices, record keeping, and which input VAT can or cannot be recovered.
    Returns the most relevant sections with their section numbers and pages."""
    passages = []
    for score, chunk in search(question):
        passages.append(f"[Section {chunk['section']}, page {chunk['page']}]\n{chunk['text']}")
    return "\n\n".join(passages)


TOOLS = [invoice_database, vat_guide]

if __name__ == "__main__":
    print(invoice_database.invoke({"question": "How much VAT did we pay in April 2026?"}))
    print()
    print(vat_guide.invoke({"question": "Can I recover VAT on a company car?"})[:300])
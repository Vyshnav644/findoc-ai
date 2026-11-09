# FinDoc AI

**AI copilot for UAE invoices and VAT.** FinDoc AI reads supplier invoice images with Gemini vision, extracts the key fields into validated structured data, and checks that the VAT adds up.

## The problem

UAE businesses reclaim input VAT from their supplier invoices in every VAT return, but most of those invoices are still typed in by hand: slow, repetitive and error-prone. With mandatory e-invoicing starting in 2027, companies are digitizing their invoice handling now.

## What works so far

- **Extraction:** sends an invoice image to Gemini and gets back a structured invoice (vendor, invoice number, date, subtotal, VAT, total), validated with a pydantic schema
- **Consistency checks:** flags an invoice if subtotal + VAT does not equal the total, or if VAT is not 5% of the subtotal
- **Evaluation:** compares each extracted field against known answers; currently 6/6 fields correct on the sample invoice
- **Configurable model:** the Gemini model is a setting (`GEMINI_MODEL`), so switching models needs no code change

## How to run

```
git clone https://github.com/Vyshnav644/findoc-ai.git
cd findoc-ai
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python read_invoice.py
```

Then put your own Gemini API key in `.env` (get one free at Google AI Studio).

The sample invoice in `samples/` is fictional and made for testing.

## Roadmap

- [x] Read invoice images with a vision LLM
- [x] Validate extracted data and measure accuracy
- [ ] Save invoices to PostgreSQL
- [ ] Ask questions in plain English (text-to-SQL)
- [ ] Answer VAT rule questions with RAG over FTA guides
- [ ] LangGraph agent, FastAPI and Docker
- [ ] Deploy to the cloud, with CI and evaluation scores
-- Invoices extracted by Gemini, one row per invoice
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    vendor_name TEXT NOT NULL,
    invoice_number TEXT NOT NULL,
    invoice_date DATE NOT NULL,
    subtotal NUMERIC(12, 2) NOT NULL,
    vat_amount NUMERIC(12, 2) NOT NULL,
    total NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Block duplicate invoices: same supplier (any capitalization) + same invoice number
CREATE UNIQUE INDEX invoices_vendor_number_unique
ON invoices (lower(vendor_name), invoice_number);
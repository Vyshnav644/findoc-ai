from dotenv import load_dotenv
from google import genai
from google.genai import types
from invoice_schema import Invoice

load_dotenv()
client = genai.Client(
    http_options=types.HttpOptions(
        timeout=30_000,
        retry_options=types.HttpRetryOptions(attempts=1),
    )
)
with open("samples/sample_invoice_01.png", "rb") as f:
    image_bytes = f.read()

print("Image loaded, size in bytes:", len(image_bytes))

image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=[image_part, "Extract the invoice details from this image."],
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=Invoice,
    ),
)
invoice = response.parsed
if invoice is None:
    raise ValueError("Gemini's reply did not match the Invoice form")
print(type(invoice))
print(invoice)
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


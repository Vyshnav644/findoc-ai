from dotenv import load_dotenv
from google import genai
from google.genai import types

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
    contents=[image_part, "What is the invoice number, the VAT amount and the total on this invoice?"],
)
print(response.text)
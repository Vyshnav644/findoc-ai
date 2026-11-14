import json
import mimetypes
import time

from invoice_pipeline import extract_invoice, check_invoice

TEST_DIR = "samples/test_set/"
FIELDS = ["vendor_name", "invoice_number", "invoice_date", "subtotal", "vat_amount", "total"]

with open(TEST_DIR + "ground_truth.json", encoding="utf-8") as f:
    truth = json.load(f)

def same(got, want):
    if isinstance(want, (int, float)):
        return abs(float(got) - want) < 0.01
    return str(got).lower().strip() == str(want).lower().strip()

total_correct = 0
total_fields = 0

for name, expected in truth.items():
    with open(TEST_DIR + name, "rb") as f:
        image_bytes = f.read()
    mime_type = mimetypes.guess_type(name)[0]

    try:
        invoice = extract_invoice(image_bytes, mime_type)
    except Exception as error:
        print(f"{name}: ERROR ({type(error).__name__}), counted as 0/6")
        total_fields += len(FIELDS)
        continue

    wrong = []
    for field in FIELDS:
        got = getattr(invoice, field)
        if same(got, expected[field]):
            total_correct += 1
        else:
            wrong.append(f"{field}: got {got}, expected {expected[field]}")
        total_fields += 1

    problems = check_invoice(invoice)
    print(f"{name}: {len(FIELDS) - len(wrong)}/{len(FIELDS)} correct, problems flagged: {len(problems)}")
    for line in wrong:
        print("   WRONG", line)

    time.sleep(5)

print(f"\nField accuracy: {total_correct}/{total_fields} ({100 * total_correct / total_fields:.0f}%)")    
import re
from pypdf import PdfReader


def clean(text):
    text = re.sub(
        r"^\s*\d+\s+VAT Guide \| Taxable Person \| VATG001\s*$",
        "",
        text,
        flags=re.MULTILINE,
    )
    text = text.replace("\uf0b7", "-")
    return text.strip()


reader = PdfReader("knowledge/fta_taxable_person_guide_2018.pdf")

pages = []
for number in range(5, len(reader.pages)):
    text = clean(reader.pages[number].extract_text())
    pages.append((number, text))

print("Content pages:", len(pages))
print(pages[34])
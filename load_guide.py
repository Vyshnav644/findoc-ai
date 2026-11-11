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

heading = re.compile(r"^(\d+(?:\.\d+)*)\.\s+(.+)$")
sections = []
current = None
chapter = 0

for number, text in pages:
    for line in text.split("\n"):
        line = line.strip()
        match = heading.match(line)

        real = False
        if match:
            section = match.group(1)
            if "." in section:
                real = section.split(".")[0] == str(chapter)
            else:
                real = int(section) == chapter + 1
                if real:
                    chapter = int(section)

        if real:
            current = {"section": section, "title": match.group(2), "page": number, "lines": []}
            sections.append(current)
        elif current is not None:
            current["lines"].append(line)

print("Sections:", len(sections))

for s in sections:
    if s["section"] == "10.6.3":
        print(s["section"], s["title"], "page", s["page"])
        print(" ".join(s["lines"]))            
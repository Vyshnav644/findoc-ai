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

chunks = []
for s in sections:
    body = " ".join(s["lines"]).strip()
    if not body:
        continue
    chunks.append({
        "section": s["section"],
        "title": s["title"],
        "page": s["page"],
        "text": f'{s["section"]} {s["title"]}\n{body}',
    })

print("Sections:", len(sections))
print("Chunks with text:", len(chunks))

sizes = [len(c["text"].split()) for c in chunks]
print("Smallest:", min(sizes), "words")
print("Largest:", max(sizes), "words")
print("Average:", sum(sizes) // len(sizes), "words")
print()
print("Chunks over 500 words:")
for c in chunks:
    words = len(c["text"].split())
    if words > 500:
        print(c["section"], c["title"], words)
print()
print("Chunks fewer than 40 words:")
for c in chunks:
    words = len(c["text"].split())
    if words < 40:
        print(c["section"], c["title"], words)
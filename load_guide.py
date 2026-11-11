import re
from pypdf import PdfReader

GUIDE_PATH = "knowledge/fta_taxable_person_guide_2018.pdf"
FIRST_CONTENT_PAGE = 5

heading = re.compile(r"^(\d+(?:\.\d+)*)\.\s+(.+)$")


def clean(text):
    text = re.sub(
        r"^\s*\d+\s+VAT Guide \| Taxable Person \| VATG001\s*$",
        "",
        text,
        flags=re.MULTILINE,
    )
    text = text.replace("\uf0b7", "-")
    return text.strip()


def load_chunks():
    reader = PdfReader(GUIDE_PATH)

    pages = []
    for number in range(FIRST_CONTENT_PAGE, len(reader.pages)):
        text = clean(reader.pages[number].extract_text())
        pages.append((number, text))

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
    return chunks


if __name__ == "__main__":
    chunks = load_chunks()
    sizes = [len(c["text"].split()) for c in chunks]
    print("Chunks:", len(chunks))
    print("Smallest:", min(sizes), "words")
    print("Largest:", max(sizes), "words")
    print("Average:", sum(sizes) // len(sizes), "words")
from config import MODEL_NAME
from llm import client
from retrieve import search

GUIDE_NAME = "FTA Taxable Person Guide (VATG001, June 2018)"

def answer_from_guide(question, top_k=3):
    results = search(question, top_k=top_k)

    passages = ""
    for score, chunk in results:
        passages += f"[Section {chunk['section']}, page {chunk['page']}]\n{chunk['text']}\n\n"
        prompt = f"""You answer UAE VAT questions for an accountant, using ONLY the passages below from the {GUIDE_NAME}.

Passages:
{passages}
Rules:
- Use only these passages. Do not use outside knowledge.
- Cite the section and page for every rule you mention, like (Section 10.6.3, page 40).
- If the passages answer the question only partly, explain what they do say, with citations, and say what they do not cover.
- Only if the passages contain nothing relevant, say exactly: The guide does not cover this.
- When a passage states a general rule that applies to the situation in the question, apply it and explain how it applies.
- Keep it short: 2 to 4 sentences.

Question: {question}"""

    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text, results

if __name__ == "__main__":
    question = input("Ask a VAT question: ")
    answer, results = answer_from_guide(question)
    print(answer)
    print()
    print("Searched:", ", ".join(chunk["section"] for score, chunk in results))
    print(f"Source: {GUIDE_NAME}. Rules may have changed since this guide was issued.")
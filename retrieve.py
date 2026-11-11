import json

from google.genai import types

from config import EMBED_MODEL
from llm import client

INDEX_PATH = "knowledge/guide_embeddings.json"

with open(INDEX_PATH, encoding="utf-8") as f:
    index = json.load(f)

def embed_question(question):
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=question,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=768,
        ),
    )
    return result.embeddings[0].values


def similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    size_a = sum(x * x for x in a) ** 0.5
    size_b = sum(x * x for x in b) ** 0.5
    return dot / (size_a * size_b) 
   
def search(question, top_k=3):
    q_vector = embed_question(question)

    scored = []
    for chunk in index:
        score = similarity(q_vector, chunk["embedding"])
        scored.append((score, chunk))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:top_k]

if __name__ == "__main__":
    question = input("Ask a VAT question: ")
    for score, chunk in search(question):
        print(round(score, 3), chunk["section"], chunk["title"], "page", chunk["page"])
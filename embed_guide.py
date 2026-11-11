from google.genai import types

from config import EMBED_MODEL
from llm import client
from load_guide import load_chunks

chunks = load_chunks()
first = chunks[0]

result = client.models.embed_content(
    model=EMBED_MODEL,
    contents=first["text"],
    config=types.EmbedContentConfig(
        task_type="RETRIEVAL_DOCUMENT",
        output_dimensionality=768,
    ),
)

vector = result.embeddings[0].values
print(first["section"], first["title"])
print("Numbers in vector:", len(vector))
print("First five:", vector[:5])
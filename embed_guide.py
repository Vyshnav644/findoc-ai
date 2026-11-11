import json
import time
from google.genai import types

from config import EMBED_MODEL
from llm import client
from load_guide import load_chunks

OUTPUT_PATH = "knowledge/guide_embeddings.json"
BATCH_SIZE = 20

chunks = load_chunks()

for start in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[start:start + BATCH_SIZE]
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=[c["text"] for c in batch],
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=768,
        ),
    )
    for c, e in zip(batch, result.embeddings):
        c["embedding"] = e.values
    print("Embedded", start + len(batch), "of", len(chunks))
    time.sleep(15)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(chunks, f)

print("Saved to", OUTPUT_PATH)
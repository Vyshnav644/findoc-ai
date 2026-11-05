import os 
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
if key is None:
    raise ValueError("GEMINI_API_KEY is missing from .env")
print("Key loaded, length:", len(key))
import os 
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("TEST_KEY")
if key is None:
    raise ValueError("TEST_KEY is missing from .env")
print(key)
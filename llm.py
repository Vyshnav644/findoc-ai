import config
from google import genai
from google.genai import types

client = genai.Client(
    http_options=types.HttpOptions(
        timeout=30_000,
        retry_options=types.HttpRetryOptions(attempts=3),
    )
)
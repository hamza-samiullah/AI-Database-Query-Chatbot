
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.getenv("MODEL_NAME", "z-ai/glm-4.5-air:free") # Using default just in case

print(f"Testing OpenRouter limits with model: {MODEL}")
print(f"Base URL: {BASE_URL}")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    # OpenRouter specific headers
    "HTTP-Referer": "http://localhost:8000",
    "X-Title": "LightChatbot"
}

payload = {
    "model": MODEL,
    "messages": [
        {"role": "user", "content": "Say hello!"}
    ]
}

try:
    response = requests.post(
        f"{BASE_URL}/chat/completions", 
        headers=headers, 
        json=payload, 
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")


import os
import requests
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("GROQ_API_KEY")
BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

print(f"Testing Groq limits with model: {MODEL}")
print(f"Base URL: {BASE_URL}")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
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

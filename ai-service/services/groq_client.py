import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

class GroqClient:

    def __init__(self):
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

    def generate(self, prompt, retries=3):
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }

        for attempt in range(retries):
            try:
                response = requests.post(self.url, headers=self.headers, json=data)

                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]

                else:
                    print("Error:", response.text)

            except Exception as e:
                print("Exception:", str(e))

            time.sleep(2 ** attempt)

        return "Fallback: AI unavailable"
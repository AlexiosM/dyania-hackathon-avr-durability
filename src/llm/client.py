import requests


class OllamaClient:
    def __init__(self, url, model):
        self.url = url
        self.model = model

    def generate(self, prompt):
        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0,
                    "num_predict": 1024
                }
            },
            timeout=600
        )

        response.raise_for_status()

        return response.json()["response"]

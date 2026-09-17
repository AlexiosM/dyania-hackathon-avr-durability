import json

import requests

from .config import (
    MAX_RETRIES,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT_SECONDS,
    OLLAMA_URL,
)


class OllamaClient:
    def __init__(
        self,
        model=OLLAMA_MODEL,
        url=OLLAMA_URL,
        timeout=OLLAMA_TIMEOUT_SECONDS,
    ):
        self.model = model
        self.url = url
        self.timeout = timeout

    def chat(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0
            },
        }

        response = requests.post(
            self.url,
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        content = data["message"]["content"]

        return json.loads(content)

    def extract_with_retry(self, messages, patient_id):
        last_error = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = self.chat(messages)

                if not isinstance(result, dict):
                    raise ValueError(
                        f"{patient_id}: LLM response is not an object"
                    )

                return result

            except Exception as exc:
                last_error = exc

                if attempt == MAX_RETRIES:
                    raise RuntimeError(
                        f"Failed to extract {patient_id} after "
                        f"{MAX_RETRIES} attempts: {last_error}"
                    ) from last_error

        raise RuntimeError(
            f"Failed to extract {patient_id}: {last_error}"
        )

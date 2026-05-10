import json
import requests
import re

from app.core.config import settings


class LLMService:

    @staticmethod
    def generate(prompt: str):

        try:

            response = requests.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.2
                },
            )

            response.raise_for_status()

            data = response.json()

            raw_result = data["response"].strip()

            # tìm JSON
            match = re.search(r'\{.*\}', raw_result, re.DOTALL)

            if not match:
                raise Exception("Không tìm thấy JSON")

            json_text = match.group()

            parsed = json.loads(json_text)

            return parsed

        except json.JSONDecodeError:
            raise Exception("AI trả JSON không hợp lệ")

        except requests.exceptions.Timeout:
            raise Exception("LLM timeout")

        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ollama")

        except Exception as e:
            raise Exception(f"LLM Error: {str(e)}")
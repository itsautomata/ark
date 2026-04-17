"""Ollama client. calls local Gemma for claim extraction and inflation scoring."""

from __future__ import annotations

import httpx

OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "gemma4:e4b"


class OllamaError(Exception):
    pass


async def generate(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.1,
    timeout: float = 120.0,
) -> str:
    """call Ollama generate endpoint. returns the response text."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                    },
                },
            )
        except httpx.ConnectError:
            raise OllamaError(
                "cannot connect to Ollama. is it running? start with: ollama serve"
            )

        if resp.status_code != 200:
            raise OllamaError(f"Ollama returned {resp.status_code}: {resp.text[:200]}")

        data = resp.json()
        return data.get("response", "")


async def is_available(model: str = DEFAULT_MODEL) -> bool:
    """check if Ollama is running and the model is pulled."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            if resp.status_code != 200:
                return False
            models = [m["name"] for m in resp.json().get("models", [])]
            return any(model in m for m in models)
    except Exception:
        return False

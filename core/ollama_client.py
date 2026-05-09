"""
MEGAN Ollama Client
Talks to local Ollama server — FREE, no API key, runs offline.
Default model: gemma4:e4b  (fast, capable, ~3GB RAM)
"""

import json
import requests
from typing import Optional

OLLAMA_BASE = "http://localhost:11434"
DEFAULT_MODEL = "gemma4:e4b"


def get_available_models() -> list:
    """Return list of models installed in Ollama."""
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        r.raise_for_status()
        return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []


def is_ollama_running() -> bool:
    try:
        requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        return True
    except Exception:
        return False


def pick_model(preferred: str = DEFAULT_MODEL) -> str:
    """Pick best available model, falling back gracefully."""
    available = get_available_models()
    if not available:
        return preferred
    # Prefer exact match
    if preferred in available:
        return preferred
    # Prefer gemma variants
    for m in available:
        if "gemma" in m.lower():
            return m
    # Any model
    return available[0]


def call_ollama(
    system_prompt: str,
    messages: list,
    user_message: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """
    Call local Ollama API.
    Returns assistant text response.
    """
    if not is_ollama_running():
        return (
            "[ERROR] Ollama is not running.\n"
            "Start it with: ollama serve\n"
            "Install from: https://ollama.com"
        )

    chosen_model = model or pick_model()

    # Build message list for /api/chat
    full_messages = [{"role": "system", "content": system_prompt}]
    full_messages.extend(messages)
    full_messages.append({"role": "user", "content": user_message})

    payload = {
        "model": chosen_model,
        "messages": full_messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        }
    }

    try:
        r = requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json=payload,
            timeout=180
        )
        r.raise_for_status()
        data = r.json()
        return data.get("message", {}).get("content", "[No response]")
    except requests.Timeout:
        return "[ERROR] Ollama timed out. Try a smaller model or increase timeout."
    except requests.HTTPError as e:
        # Model not found — suggest pull
        if e.response.status_code == 404:
            return (
                f"[ERROR] Model '{chosen_model}' not found in Ollama.\n"
                f"Pull it with: ollama pull {chosen_model}\n"
                f"Available models: {', '.join(get_available_models()) or 'none'}"
            )
        return f"[ERROR] Ollama HTTP {e.response.status_code}: {e.response.text[:300]}"
    except Exception as e:
        return f"[ERROR] {e}"


def stream_ollama(
    system_prompt: str,
    messages: list,
    user_message: str,
    model: Optional[str] = None,
    on_token=None,
):
    """
    Stream tokens from Ollama.
    on_token(chunk: str) called for each token.
    Returns full response string.
    """
    if not is_ollama_running():
        msg = "[ERROR] Ollama is not running. Start with: ollama serve"
        if on_token:
            on_token(msg)
        return msg

    chosen_model = model or pick_model()
    full_messages = [{"role": "system", "content": system_prompt}]
    full_messages.extend(messages)
    full_messages.append({"role": "user", "content": user_message})

    payload = {
        "model": chosen_model,
        "messages": full_messages,
        "stream": True,
        "options": {"temperature": 0.7}
    }

    full_text = []
    try:
        with requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json=payload,
            stream=True,
            timeout=180
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        full_text.append(token)
                        if on_token:
                            on_token(token)
                    if chunk.get("done"):
                        break
    except Exception as e:
        err = f"[ERROR] {e}"
        if on_token:
            on_token(err)
        return err

    return "".join(full_text)

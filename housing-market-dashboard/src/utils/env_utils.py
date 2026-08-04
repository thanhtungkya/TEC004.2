"""
env_utils.py
Environment variables management and AI provider configuration persistence.

Features:
    - Reads AI provider settings, API keys, models, and custom endpoints
    - Safely writes and updates settings in root .env configuration file
    - Masking of sensitive API keys for secure UI representation

Dependencies:
    - os, pathlib.Path: File & environment variables access

Exports:
    - get_ai_config(): Returns dictionary with active AI configurations
    - save_ai_config(provider, api_key, model, custom_endpoint): Updates .env and runtime os.environ
"""

import os
from pathlib import Path
from typing import Dict, Any

# Find root project directory (.env location)
BASE_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = BASE_DIR / ".env"



def get_ai_config() -> Dict[str, Any]:
    """Retrieves current AI provider configuration from environment variables.

    Returns:
        Dict[str, Any]: Dictionary containing:
            - provider: Active provider name ('chatgpt', 'claude', 'gemini')
            - api_key: Masked API key string for safe UI presentation
            - raw_api_key: Full unmasked API key string
            - model: Target model ID
            - custom_endpoint: Optional custom proxy/base URL
            - has_key: Boolean indicating whether API key is present
    """
    provider = os.getenv("AI_PROVIDER", "chatgpt").lower()
    api_key = os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
    model = os.getenv("AI_MODEL", "")
    custom_endpoint = os.getenv("AI_CUSTOM_ENDPOINT", "")

    # Default models if not specified
    if not model:
        if provider == "chatgpt":
            model = "gpt-5.6-sol"
        elif provider == "claude":
            model = "claude-sonnet-5"
        elif provider == "gemini":
            model = "gemini-3.5-flash"
        else:
            model = "gpt-5.6-sol"

    masked_key = ""
    if api_key:
        if len(api_key) > 8:
            masked_key = f"{api_key[:4]}...{api_key[-4:]}"
        else:
            masked_key = "********"

    return {
        "provider": provider,
        "api_key": masked_key,
        "raw_api_key": api_key,
        "model": model,
        "custom_endpoint": custom_endpoint,
        "has_key": bool(api_key),
    }


def save_ai_config(provider: str, api_key: str, model: str, custom_endpoint: str = "") -> bool:
    """Saves AI provider configuration into root .env file and updates os.environ.

    Args:
        provider: Selected AI provider name ('chatgpt', 'claude', 'gemini').
        api_key: API key string (if masked string starting with '***' is passed, key is preserved).
        model: Selected model identifier.
        custom_endpoint: Optional custom base endpoint URL.

    Returns:
        bool: True if configuration was successfully saved.
    """

    env_vars = {}
    
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()

    # Update AI config keys
    env_vars["AI_PROVIDER"] = provider
    if api_key and not api_key.startswith("***"):  # Only update key if real key provided
        env_vars["AI_API_KEY"] = api_key
        env_vars["OPENAI_API_KEY"] = api_key
        os.environ["AI_API_KEY"] = api_key
        os.environ["OPENAI_API_KEY"] = api_key

    env_vars["AI_MODEL"] = model
    env_vars["AI_CUSTOM_ENDPOINT"] = custom_endpoint

    os.environ["AI_PROVIDER"] = provider
    os.environ["AI_MODEL"] = model
    os.environ["AI_CUSTOM_ENDPOINT"] = custom_endpoint

    # Write back to .env
    lines = []
    for k, v in env_vars.items():
        lines.append(f"{k}={v}\n")

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return True

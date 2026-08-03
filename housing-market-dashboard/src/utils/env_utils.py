import os
from pathlib import Path

# Find root project directory (.env location)
BASE_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = BASE_DIR / ".env"

def get_ai_config():
    """Retrieve AI configuration from environment variables."""
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
    """Save AI configuration into root .env file and update os.environ."""
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

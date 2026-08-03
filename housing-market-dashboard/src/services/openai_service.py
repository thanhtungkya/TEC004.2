import os
import json
import logging
from typing import List, Dict
import requests
from openai import OpenAI
from dotenv import load_dotenv
from src.utils.env_utils import get_ai_config

load_dotenv()

logger = logging.getLogger(__name__)


def _build_prompt(properties: List[Dict]) -> str:
    prompt_data = []
    for p in properties:
        prompt_data.append({
            "id": p["id"],
            "district": p.get("district", ""),
            "area": p.get("area", 0),
            "property_type": p.get("property_type", ""),
            "listed_price": p.get("price", 0)
        })

    return (
        "You are a real estate AI expert for Hanoi market. "
        "Based on the following properties data (ID, district, area in m2, property type, listed price in billion VND), "
        "predict the fair market value (in billion VND) for each property.\n"
        "Return a JSON object where keys are the property IDs (as strings) and values are the predicted prices as floats. "
        "Do not include any Markdown formatting or extra text outside JSON.\n\n"
        f"Properties: {json.dumps(prompt_data, ensure_ascii=False)}"
    )


def _predict_openai(prompt: str, api_key: str, model: str, base_url: str = None) -> str:
    client_kwargs = {"api_key": api_key or "sk-dummy"}
    if base_url:
        client_kwargs["base_url"] = base_url

    client = OpenAI(**client_kwargs)
    response = client.chat.completions.create(
        model=model or "gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a real estate assistant. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content


def _predict_claude(prompt: str, api_key: str, model: str) -> str:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": model or "claude-3-5-haiku-20241022",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["content"][0]["text"]


def _predict_gemini(prompt: str, api_key: str, model: str) -> str:
    selected_model = model or "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def predict_prices(properties: List[Dict]) -> Dict[int, float]:
    """
    Given a list of properties, predict fair market price using configured AI provider.
    Returns a dict mapping property ID to predicted price.
    """
    ai_config = get_ai_config()
    provider = ai_config["provider"]
    api_key = ai_config["raw_api_key"]
    model = ai_config["model"]
    custom_endpoint = ai_config["custom_endpoint"]

    if not api_key and provider != "custom":
        logger.error(f"API key is not configured for provider: {provider}")
        return {}

    results = {}
    batch_size = 10

    for i in range(0, len(properties), batch_size):
        batch = properties[i:i+batch_size]
        prompt = _build_prompt(batch)

        try:
            if provider == "claude":
                content = _predict_claude(prompt, api_key, model)
            elif provider == "gemini":
                content = _predict_gemini(prompt, api_key, model)
            elif provider == "custom":
                content = _predict_openai(prompt, api_key, model, base_url=custom_endpoint)
            else:
                # Default: chatgpt / openai
                content = _predict_openai(prompt, api_key, model)

            # Strip markdown codeblocks if AI returned ```json ... ```
            content_clean = content.strip()
            if content_clean.startswith("```"):
                lines = content_clean.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                content_clean = "\n".join(lines).strip()

            predictions = json.loads(content_clean)
            for pid_str, price in predictions.items():
                results[int(pid_str)] = float(price)
        except Exception as exc:
            logger.error(f"AI prediction error with provider {provider}: {exc}")

    return results

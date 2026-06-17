import os
import json
import logging
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def predict_prices(properties: List[Dict]) -> Dict[int, float]:
    """
    Given a list of properties, predict the fair market price.
    Returns a dict mapping property ID to predicted price.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY is not set.")
        return {}

    client = OpenAI(api_key=api_key)
    results = {}
    batch_size = 10
    
    for i in range(0, len(properties), batch_size):
        batch = properties[i:i+batch_size]
        prompt_data = []
        for p in batch:
            prompt_data.append({
                "id": p["id"],
                "district": p.get("district", ""),
                "area": p.get("area", 0),
                "property_type": p.get("property_type", ""),
                "listed_price": p.get("price", 0)
            })

        prompt = (
            "You are a real estate AI expert for Hanoi market. "
            "Based on the following properties data (ID, district, area in m2, property type, listed price in billion VND), "
            "predict the fair market value (in billion VND) for each property.\n"
            "Return a JSON object where keys are the property IDs (as strings) and values are the predicted prices as floats. "
            "Do not include any other text.\n\n"
            f"Properties: {json.dumps(prompt_data)}"
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful real estate assistant. Respond only with JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            content = response.choices[0].message.content
            predictions = json.loads(content)
            for pid_str, price in predictions.items():
                results[int(pid_str)] = float(price)
        except Exception as e:
            logger.error(f"OpenAI prediction error: {e}")

    return results

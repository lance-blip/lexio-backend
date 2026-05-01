import httpx
import asyncio
from typing import Dict, Any, List, Optional
from config import config
import logging

logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self):
        self.base_url = config.OPENROUTER_BASE_URL
        self.api_key = config.OPENROUTER_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://lexio.co.za",
            "X-Title": "Lexio",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=30.0)
        self.models = [config.DEFAULT_MODEL, config.FALLBACK_MODEL]

    async def chat_completion(self, messages: List[Dict[str, str]], model: str = None) -> Optional[str]:
        """Send chat completion request to OpenRouter with fallback models"""
        if model is None:
            model = config.DEFAULT_MODEL
            
        for attempt_model in self.models:
            try:
                payload = {
                    "model": attempt_model,
                    "messages": messages,
                    "temperature": 0.1,
                    "max_tokens": 2000
                }
                
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                response.raise_for_status()
                data = response.json()
                
                if "choices" in data and data["choices"]:
                    return data["choices"][0]["message"]["content"]
                
            except httpx.HTTPStatusError as e:
                if response.status_code == 429:
                    logger.warning(f"Rate limit hit for model {attempt_model}, trying next...")
                    await asyncio.sleep(2)
                    continue
                logger.error(f"HTTP error {response.status_code} for model {attempt_model}: {e}")
            except Exception as e:
                logger.error(f"Error with model {attempt_model}: {e}")
                continue
        
        logger.error("All models failed")
        return None

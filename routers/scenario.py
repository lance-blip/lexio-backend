from fastapi import APIRouter, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from models.requests import ScenarioRequest
from models.responses import ScenarioResponse, ApplicableLaw, NextStep
from services.openrouter import OpenRouterClient
from services.legal_context import LegalContextManager
import json

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
context_manager = LegalContextManager()
openrouter = OpenRouterClient()

@router.post("/scenario", response_model=ScenarioResponse)
@limiter.limit("10/hour")
async def scenario_endpoint(request: ScenarioRequest, req: Request):
    # Get all legal context for comprehensive analysis
    legal_context = context_manager.get_all_context()
    
    # Load scenario system prompt
    with open("prompts/system_scenario.txt", "r") as f:
        system_prompt = f.read().replace("{legal_context}", legal_context)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.scenario}
    ]
    
    response_content = await openrouter.chat_completion(messages)
    
    if not response_content:
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable")
    
    # Try to parse structured JSON response
    try:
        # Clean up response - remove markdown code blocks if present
        cleaned = response_content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        parsed = json.loads(cleaned)
        
        return ScenarioResponse(
            applicableLaws=[ApplicableLaw(**law) for law in parsed.get("applicableLaws", [])],
            analysis=parsed.get("analysis", response_content),
            potentialViolations=parsed.get("potentialViolations", []),
            rights=parsed.get("rights", []),
            nextSteps=[NextStep(**step) for step in parsed.get("nextSteps", [])]
        )
    except (json.JSONDecodeError, Exception):
        # Fallback: return raw response as analysis
        return ScenarioResponse(
            applicableLaws=[],
            analysis=response_content,
            potentialViolations=[],
            rights=[],
            nextSteps=[
                NextStep(
                    action="Contact Legal Aid SA",
                    description="Get free legal assistance",
                    contactInfo="0800 110 110",
                    url="https://www.legal-aid.co.za"
                )
            ]
        )

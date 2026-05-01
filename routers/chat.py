from fastapi import APIRouter, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from models.requests import ChatRequest
from models.responses import ChatResponse
from services.openrouter import OpenRouterClient
from services.legal_context import LegalContextManager
import uuid

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
context_manager = LegalContextManager()
openrouter = OpenRouterClient()

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/hour")
async def chat_endpoint(request: ChatRequest, req: Request):
    # Get relevant legal context
    legal_context = context_manager.get_relevant_context(request.message)
    
    # Load system prompt
    with open("prompts/system_chat.txt", "r") as f:
        system_prompt = f.read().replace("{legal_context}", legal_context)
    
    # Build messages
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history
    if request.conversation_history:
        for msg in request.conversation_history:
            messages.append({"role": msg.role, "content": msg.content})
    
    # Add current message
    messages.append({"role": "user", "content": request.message})
    
    # Call OpenRouter
    response_content = await openrouter.chat_completion(messages)
    
    if not response_content:
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable")
    
    return ChatResponse(
        message=response_content,
        citations=[],
        confidence="HIGH",
        suggestedFollowUps=[
            "What are my next steps?",
            "What are the exceptions to this rule?",
            "How do I enforce this right?"
        ],
        conversationId=str(uuid.uuid4())
    )

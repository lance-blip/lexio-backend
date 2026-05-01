from pydantic import BaseModel
from typing import List, Optional
import uuid

class Citation(BaseModel):
    actName: str
    actNumber: str
    section: str
    subsection: Optional[str] = None
    fullReference: str
    shortReference: str
    fullText: str

class ChatResponse(BaseModel):
    message: str
    citations: List[Citation]
    confidence: str
    suggestedFollowUps: List[str]
    conversationId: str = str(uuid.uuid4())

class ApplicableLaw(BaseModel):
    actName: str
    sections: List[str]
    relevance: str

class NextStep(BaseModel):
    action: str
    description: str
    contactInfo: Optional[str] = None
    url: Optional[str] = None

class ScenarioResponse(BaseModel):
    applicableLaws: List[ApplicableLaw]
    analysis: str
    potentialViolations: List[str]
    rights: List[str]
    nextSteps: List[NextStep]

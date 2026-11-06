from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class TicketInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=2000)


class TicketClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: Literal["billing", "technical", "account", "general"]
    priority: Literal["low", "medium", "high"]
    recommended_action: Literal["reply", "investigate", "escalate"]
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(min_length=1, max_length=500)

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Literal


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    ui_type: Optional[str] = None
    data: Optional[Any] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str = "default"
    history: List[Message] = []


class Hotel(BaseModel):
    name: str
    price_per_night: float
    rating: float
    location: str
    image_url: str = ""


class Flight(BaseModel):
    airline: str
    flight_number: str
    departure: str
    arrival: str
    price: float
    duration: str


class TrackingInfo(BaseModel):
    order_id: str
    status: str
    estimated_delivery: str
    current_location: str


class RefundInfo(BaseModel):
    order_id: str
    refund_amount: float
    status: str
    estimated_days: int


class ToolResult(BaseModel):
    intent: str
    tool: str
    result: Any
    summary: str


class ChatResponse(BaseModel):
    reply: str
    ui_type: Optional[str] = None
    data: Optional[Any] = None
    intent: str
    conversation_id: str

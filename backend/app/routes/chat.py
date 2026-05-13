import logging
from fastapi import APIRouter, HTTPException
from app.schemas.models import ChatRequest, ChatResponse, Message
from app.services.memory_service import memory
from app.services.llm_service import classify_and_extract

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    logger.info("Chat request [%s]: %s", request.conversation_id, request.message[:50])

    history = memory.get_history(request.conversation_id)
    context_lines = []
    for msg in history[-4:]:
        role = "User" if msg.role == "user" else "Assistant"
        context_lines.append(f"{role}: {msg.content}")
    conversation_context = "\n".join(context_lines)

    llm_result = await classify_and_extract(
        user_message=request.message,
        conversation_context=conversation_context,
    )

    memory.add_message(request.conversation_id, Message(role="user", content=request.message))
    memory.add_message(
        request.conversation_id,
        Message(
            role="assistant",
            content=llm_result["reply"],
            ui_type=llm_result.get("ui_type"),
            data=llm_result.get("data"),
        ),
    )

    return ChatResponse(
        reply=llm_result["reply"],
        ui_type=llm_result.get("ui_type"),
        data=llm_result.get("data"),
        intent=llm_result["intent"],
        conversation_id=request.conversation_id,
    )

import logging
from typing import Dict, List
from app.schemas.models import Message

logger = logging.getLogger(__name__)

MAX_HISTORY_TURNS = 5
MAX_HISTORY_LENGTH = MAX_HISTORY_TURNS * 2


class ConversationMemory:
    def __init__(self):
        self._store: Dict[str, List[Message]] = {}

    def get_history(self, conversation_id: str) -> List[Message]:
        return self._store.get(conversation_id, [])

    def add_message(self, conversation_id: str, message: Message):
        if conversation_id not in self._store:
            self._store[conversation_id] = []
        self._store[conversation_id].append(message)
        if len(self._store[conversation_id]) > MAX_HISTORY_LENGTH:
            self._store[conversation_id] = self._store[conversation_id][-MAX_HISTORY_LENGTH:]
        logger.debug("Memory[%s] now has %d turns", conversation_id, len(self._store[conversation_id]) // 2)

    def clear(self, conversation_id: str):
        self._store.pop(conversation_id, None)
        logger.info("Cleared memory for conversation %s", conversation_id)


memory = ConversationMemory()

import logging
from collections import deque
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

DEFAULT_MAX_MESSAGES = 20


@dataclass
class Message:
    role: str  # "user", "assistant", "system"
    content: str
    metadata: dict = field(default_factory=dict)


class WorkingMemory:
    """In-memory conversation buffer for the current session."""

    def __init__(self, max_messages: int = DEFAULT_MAX_MESSAGES):
        self.max_messages = max_messages
        self._messages: deque[Message] = deque(maxlen=max_messages)
        self._session_id: str = ""

    @property
    def messages(self) -> list[Message]:
        return list(self._messages)

    @property
    def count(self) -> int:
        return len(self._messages)

    def add(self, role: str, content: str, **metadata) -> None:
        msg = Message(role=role, content=content, metadata=metadata)
        self._messages.append(msg)
        logger.debug("WorkingMemory add: role=%s len=%d", role, len(content))

    def get_context_window(self, last_n: int | None = None) -> list[dict]:
        """Return messages in OpenAI-compatible format for LLM context."""
        msgs = list(self._messages)
        if last_n:
            msgs = msgs[-last_n:]
        return [{"role": m.role, "content": m.content} for m in msgs]

    def get_user_queries(self) -> list[str]:
        return [m.content for m in self._messages if m.role == "user"]

    def clear(self) -> None:
        self._messages.clear()

    def trim_to(self, keep_last: int) -> list[Message]:
        """Remove old messages, return the removed ones (for summarization)."""
        if len(self._messages) <= keep_last:
            return []
        removed = []
        while len(self._messages) > keep_last:
            removed.append(self._messages.popleft())
        return removed

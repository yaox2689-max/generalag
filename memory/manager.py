import logging

from memory.longterm import LongTermMemory
from memory.summary import SummaryMemory
from memory.working import WorkingMemory

logger = logging.getLogger(__name__)

SUMMARIZE_THRESHOLD = 15  # Summarize when working memory exceeds this


class MemoryManager:
    """Coordinates working, summary, and long-term memory layers."""

    def __init__(self):
        self.working = WorkingMemory()
        self.summary = SummaryMemory()
        self.longterm = LongTermMemory()

    async def on_user_message(self, query: str) -> None:
        self.working.add("user", query)
        if self.working.count > SUMMARIZE_THRESHOLD:
            await self._compress()

    async def on_agent_response(self, answer: str) -> None:
        self.working.add("assistant", answer)

    def get_context_for_llm(self, query: str) -> str:
        parts = []
        summary_ctx = self.summary.get_context_for_llm()
        if summary_ctx:
            parts.append(summary_ctx)
        return "\n\n".join(parts) if parts else ""

    def get_messages_for_llm(self, last_n: int = 10) -> list[dict]:
        return self.working.get_context_window(last_n=last_n)

    async def store_fact(self, content: str, category: str = "general", session_id: str = "") -> None:
        await self.longterm.store(content, category=category, session_id=session_id)

    async def recall(self, query: str, top_k: int = 3) -> list[dict]:
        return await self.longterm.retrieve(query, top_k=top_k)

    async def _compress(self) -> None:
        removed = self.working.trim_to(keep_last=5)
        if removed:
            await self.summary.summarize_messages(removed)
            logger.info("Compressed %d messages into summary", len(removed))

    def clear(self) -> None:
        self.working.clear()
        self.summary.clear()

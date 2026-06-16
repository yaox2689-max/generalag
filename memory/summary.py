import logging

from langchain_core.messages import HumanMessage, SystemMessage

from agent.llm import get_llm
from memory.working import Message

logger = logging.getLogger(__name__)

SUMMARIZE_PROMPT = """You are a conversation summarizer. Compress the following messages into a concise summary that preserves:
- Key facts and decisions
- User preferences mentioned
- Important context for future reference

Messages:
{messages}

Output a concise summary (3-5 sentences) in the same language as the messages."""


class SummaryMemory:
    """Compressed conversation summaries to preserve long-term context."""

    def __init__(self):
        self._summaries: list[str] = []

    @property
    def summaries(self) -> list[str]:
        return list(self._summaries)

    @property
    def count(self) -> int:
        return len(self._summaries)

    def add(self, summary: str) -> None:
        self._summaries.append(summary)
        logger.info("SummaryMemory add: %s...", summary[:80])

    def get_combined(self) -> str:
        if not self._summaries:
            return ""
        return "\n\n".join(f"[Summary {i+1}] {s}" for i, s in enumerate(self._summaries))

    def get_context_for_llm(self) -> str:
        """Return summary context to inject into system prompt."""
        if not self._summaries:
            return ""
        return f"Previous conversation context:\n{self.get_combined()}"

    async def summarize_messages(self, messages: list[Message]) -> str:
        """Use LLM to compress messages into a summary."""
        if not messages:
            return ""

        formatted = "\n".join(f"[{m.role}] {m.content}" for m in messages)
        llm = get_llm()

        resp = await llm.ainvoke([
            SystemMessage(content=SUMMARIZE_PROMPT.format(messages=formatted)),
            HumanMessage(content="Summarize now."),
        ])

        summary = resp.content.strip()
        self.add(summary)
        return summary

    def clear(self) -> None:
        self._summaries.clear()

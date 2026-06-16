import asyncio
import functools
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 3


@dataclass
class ToolResult:
    success: bool
    output: str
    metadata: dict = field(default_factory=dict)
    error: str | None = None
    elapsed_ms: int = 0


class BaseTool(ABC):
    name: str
    description: str
    parameters: dict  # JSON Schema

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        ...

    async def __call__(self, **kwargs) -> ToolResult:
        start = time.monotonic()
        last_error = None

        for attempt in range(1, DEFAULT_MAX_RETRIES + 1):
            try:
                result = await asyncio.wait_for(
                    self.execute(**kwargs), timeout=DEFAULT_TIMEOUT
                )
                result.elapsed_ms = int((time.monotonic() - start) * 1000)
                logger.info(
                    "tool=%s attempt=%d elapsed_ms=%d success=%s",
                    self.name, attempt, result.elapsed_ms, result.success,
                )
                return result
            except asyncio.TimeoutError:
                last_error = f"Timeout after {DEFAULT_TIMEOUT}s"
                logger.warning("tool=%s attempt=%d timeout", self.name, attempt)
            except Exception as e:
                last_error = str(e)
                logger.warning("tool=%s attempt=%d error=%s", self.name, attempt, e)

        elapsed_ms = int((time.monotonic() - start) * 1000)
        return ToolResult(
            success=False,
            output="",
            error=f"Failed after {DEFAULT_MAX_RETRIES} retries: {last_error}",
            elapsed_ms=elapsed_ms,
        )

    def to_langchain_tool(self):
        from langchain_core.tools import StructuredTool

        async def _run(**kwargs):
            result = await self(**kwargs)
            return result.output

        return StructuredTool.from_function(
            coroutine=_run,
            name=self.name,
            description=self.description,
            args_schema=self.parameters,
        )

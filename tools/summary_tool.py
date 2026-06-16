from langchain_openai import ChatOpenAI

from config import settings
from tools.base import BaseTool, ToolResult

SUMMARIZE_PROMPT = (
    "You are a concise summarizer. "
    "Summarize the following text in 3-5 bullet points, keeping key facts and numbers.\n\n"
    "Text:\n{text}"
)


class SummaryTool(BaseTool):
    name = "text_summarizer"
    description = "Summarize a long piece of text into concise bullet points using LLM."
    parameters = {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to summarize",
            },
            "language": {
                "type": "string",
                "description": "Output language: 'zh' for Chinese, 'en' for English (default 'zh')",
                "default": "zh",
            },
        },
        "required": ["text"],
    }

    async def execute(self, text: str, language: str = "zh", **kwargs) -> ToolResult:
        try:
            llm = ChatOpenAI(
                model=settings.llm_model,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                temperature=0,
            )
            prompt = SUMMARIZE_PROMPT.format(text=text)
            if language == "zh":
                prompt += "\n请用中文输出。"

            resp = await llm.ainvoke(prompt)
            return ToolResult(success=True, output=resp.content)
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

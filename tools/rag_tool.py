from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pymilvus import Collection, connections

from config import settings
from tools.base import BaseTool, ToolResult

RAG_COLLECTION = "general_knowledge"


class RAGTool(BaseTool):
    name = "rag_search"
    description = "Search the local knowledge base (Milvus vector store) for relevant documents."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query to find relevant documents",
            },
            "top_k": {
                "type": "integer",
                "description": "Number of results to return (default 5)",
                "default": 5,
            },
        },
        "required": ["query"],
    }

    def _ensure_connection(self):
        try:
            connections.connect(alias="default", uri=settings.milvus_uri)
        except Exception:
            pass  # already connected

    async def execute(self, query: str, top_k: int = 5, **kwargs) -> ToolResult:
        try:
            self._ensure_connection()

            embeddings = OpenAIEmbeddings(
                openai_api_key=settings.openai_api_key,
                openai_api_base=settings.openai_base_url,
            )
            query_vec = embeddings.embed_query(query)

            collection = Collection(RAG_COLLECTION)
            collection.load()

            results = collection.search(
                data=[query_vec],
                anns_field="embedding",
                param={"metric_type": "COSINE", "params": {"nprobe": 16}},
                limit=top_k,
                output_fields=["text", "source"],
            )

            formatted = []
            for hit in results[0]:
                text = hit.entity.get("text", "")
                source = hit.entity.get("source", "unknown")
                score = hit.score
                formatted.append(f"[score={score:.3f}] ({source})\n{text}")

            output = "\n\n---\n\n".join(formatted) if formatted else "No relevant documents found."
            return ToolResult(
                success=True,
                output=output,
                metadata={"num_results": len(formatted)},
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"RAG search failed (is Milvus running?): {e}",
            )

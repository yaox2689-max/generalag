import hashlib
import logging

from langchain_openai import OpenAIEmbeddings
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections

from config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "agent_longterm_memory"
DIMENSION = 1536


def _connect():
    try:
        connections.connect(alias="default", uri=settings.milvus_uri)
    except Exception:
        pass


def _ensure_collection() -> Collection:
    _connect()
    if Collection(name=COLLECTION_NAME).exists():
        return Collection(COLLECTION_NAME)

    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=64),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4096),
        FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=64),
        FieldSchema(name="session_id", dtype=DataType.VARCHAR, max_length=128),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
    ]
    schema = CollectionSchema(fields, description="Agent long-term memory")
    collection = Collection(COLLECTION_NAME, schema)
    collection.create_index(
        "embedding",
        {"metric_type": "COSINE", "index_type": "IVF_FLAT", "params": {"nlist": 128}},
    )
    return collection


def _make_id(content: str, category: str) -> str:
    return hashlib.md5(f"{category}:{content[:200]}".encode()).hexdigest()


class LongTermMemory:
    """Persistent vector memory for cross-session knowledge."""

    def __init__(self):
        self._embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_base_url,
        )

    async def store(
        self,
        content: str,
        category: str = "general",
        session_id: str = "",
    ) -> str:
        collection = _ensure_collection()
        mem_id = _make_id(content, category)
        vector = self._embeddings.embed_query(content)
        collection.insert([[mem_id], [content], [category], [session_id], [vector]])
        collection.flush()
        logger.info("LongTermMemory store: category=%s len=%d", category, len(content))
        return mem_id

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        category: str | None = None,
        score_threshold: float = 0.3,
    ) -> list[dict]:
        collection = _ensure_collection()
        collection.load()

        query_vec = self._embeddings.embed_query(query)

        results = collection.search(
            data=[query_vec],
            anns_field="embedding",
            param={"metric_type": "COSINE", "params": {"nprobe": 16}},
            limit=top_k,
            output_fields=["content", "category", "session_id"],
        )

        hits = []
        for hit in results[0]:
            if hit.score < score_threshold:
                continue
            cat = hit.entity.get("category", "")
            if category and cat != category:
                continue
            hits.append({
                "content": hit.entity.get("content", ""),
                "category": cat,
                "session_id": hit.entity.get("session_id", ""),
                "score": round(hit.score, 4),
            })

        logger.info("LongTermMemory retrieve: query=%s hits=%d", query[:50], len(hits))
        return hits

    def get_context_for_llm(self, query: str, top_k: int = 3) -> str:
        """Synchronous wrapper for retrieving memory context."""
        import asyncio
        try:
            hits = asyncio.run(self.retrieve(query, top_k=top_k))
        except RuntimeError:
            # Already in an event loop — can't use asyncio.run
            return ""
        if not hits:
            return ""
        lines = [f"- {h['content']}" for h in hits]
        return "Relevant memories:\n" + "\n".join(lines)

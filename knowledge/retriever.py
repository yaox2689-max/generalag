import logging

from langchain_openai import OpenAIEmbeddings
from pymilvus import Collection, connections

from config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "general_knowledge"


def _connect():
    try:
        connections.connect(alias="default", uri=settings.milvus_uri)
    except Exception:
        pass


async def retrieve(
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.3,
) -> list[dict]:
    _connect()

    collection = Collection(COLLECTION_NAME)
    if not collection.exists():
        return []

    collection.load()

    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.openai_api_key,
        openai_api_base=settings.openai_base_url,
    )
    query_vec = embeddings.embed_query(query)

    results = collection.search(
        data=[query_vec],
        anns_field="embedding",
        param={"metric_type": "COSINE", "params": {"nprobe": 16}},
        limit=top_k,
        output_fields=["text", "source"],
    )

    hits = []
    for hit in results[0]:
        if hit.score < score_threshold:
            continue
        hits.append({
            "text": hit.entity.get("text", ""),
            "source": hit.entity.get("source", "unknown"),
            "score": round(hit.score, 4),
        })

    logger.info("Retrieved %d chunks (query=%s, top_k=%d)", len(hits), query[:50], top_k)
    return hits

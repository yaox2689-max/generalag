import hashlib
import logging
import pathlib

from langchain_openai import OpenAIEmbeddings
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections

from config import settings
from knowledge.chunker import Chunk, ChunkingConfig, chunk_text

logger = logging.getLogger(__name__)

COLLECTION_NAME = "general_knowledge"
DIMENSION = 1536  # text-embedding-3-small


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
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=8192),
        FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
    ]
    schema = CollectionSchema(fields, description="General knowledge base")
    collection = Collection(COLLECTION_NAME, schema)
    collection.create_index("embedding", {"metric_type": "COSINE", "index_type": "IVF_FLAT", "params": {"nlist": 128}})
    return collection


def _chunk_id(source: str, index: int, text: str) -> str:
    raw = f"{source}:{index}:{text[:100]}"
    return hashlib.md5(raw.encode()).hexdigest()


def read_file(path: str | pathlib.Path) -> tuple[str, str]:
    path = pathlib.Path(path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    elif suffix in (".txt", ".md", ".csv"):
        text = path.read_text(encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    return text, str(path)


async def ingest_file(
    path: str | pathlib.Path,
    chunk_config: ChunkingConfig | None = None,
) -> int:
    text, source = read_file(path)
    chunks = chunk_text(text, source=source, config=chunk_config)
    return await _store_chunks(chunks)


async def ingest_text(
    text: str,
    source: str = "manual",
    chunk_config: ChunkingConfig | None = None,
) -> int:
    chunks = chunk_text(text, source=source, config=chunk_config)
    return await _store_chunks(chunks)


async def _store_chunks(chunks: list[Chunk]) -> int:
    if not chunks:
        return 0

    collection = _ensure_collection()
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.openai_api_key,
        openai_api_base=settings.openai_base_url,
    )

    ids = []
    texts = []
    sources = []

    for chunk in chunks:
        cid = _chunk_id(chunk.metadata.get("source", ""), chunk.index, chunk.text)
        ids.append(cid)
        texts.append(chunk.text)
        sources.append(chunk.metadata.get("source", ""))

    vectors = embeddings.embed_documents(texts)

    collection.insert([ids, texts, sources, vectors])
    collection.flush()
    logger.info("Ingested %d chunks", len(chunks))
    return len(chunks)

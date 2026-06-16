from dataclasses import dataclass, field

from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)
    index: int = 0


@dataclass
class ChunkingConfig:
    chunk_size: int = 512
    chunk_overlap: int = 64
    separators: list[str] | None = None


DEFAULT_SEPARATORS = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", "；", ";", " "]


def chunk_text(
    text: str,
    source: str = "",
    config: ChunkingConfig | None = None,
) -> list[Chunk]:
    if config is None:
        config = ChunkingConfig()

    separators = config.separators or DEFAULT_SEPARATORS
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
        separators=separators,
    )

    raw_chunks = splitter.split_text(text)
    return [
        Chunk(
            text=chunk,
            metadata={"source": source, "chunk_index": i},
            index=i,
        )
        for i, chunk in enumerate(raw_chunks)
    ]

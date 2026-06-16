import json
import logging
import pathlib
from dataclasses import asdict, dataclass, field

logger = logging.getLogger(__name__)

DEFAULT_DIR = pathlib.Path("data/golden_samples")


@dataclass
class GoldenSample:
    id: str
    query: str
    expected_answer: str
    domain: str  # finance, qa, general, etc.
    tags: list[str] = field(default_factory=list)
    expected_tools: list[str] = field(default_factory=list)


@dataclass
class EvalResult:
    sample_id: str
    domain: str
    actual_answer: str
    scores: dict[str, float]  # dimension -> score
    passed: bool
    elapsed_ms: int


class GoldenSampleManager:
    def __init__(self, data_dir: str | pathlib.Path | None = None):
        self.data_dir = pathlib.Path(data_dir) if data_dir else DEFAULT_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _domain_file(self, domain: str) -> pathlib.Path:
        return self.data_dir / f"{domain}.json"

    def load(self, domain: str) -> list[GoldenSample]:
        path = self._domain_file(domain)
        if not path.exists():
            return []
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [GoldenSample(**item) for item in raw]

    def load_all(self) -> list[GoldenSample]:
        samples = []
        for f in self.data_dir.glob("*.json"):
            domain = f.stem
            samples.extend(self.load(domain))
        return samples

    def save(self, samples: list[GoldenSample], domain: str) -> None:
        path = self._domain_file(domain)
        data = [asdict(s) for s in samples]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Saved %d samples for domain=%s", len(samples), domain)

    def add(self, sample: GoldenSample) -> None:
        samples = self.load(sample.domain)
        # Deduplicate by id
        samples = [s for s in samples if s.id != sample.id]
        samples.append(sample)
        self.save(samples, sample.domain)

    def remove(self, sample_id: str, domain: str) -> bool:
        samples = self.load(domain)
        before = len(samples)
        samples = [s for s in samples if s.id != sample_id]
        if len(samples) < before:
            self.save(samples, domain)
            return True
        return False

    def list_domains(self) -> list[str]:
        return [f.stem for f in self.data_dir.glob("*.json")]

    def count(self, domain: str | None = None) -> int:
        if domain:
            return len(self.load(domain))
        return len(self.load_all())

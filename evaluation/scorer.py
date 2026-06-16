import logging

from langchain_core.messages import HumanMessage, SystemMessage

from agent.llm import get_llm
from evaluation.golden_sample import EvalResult, GoldenSample

logger = logging.getLogger(__name__)

SCORER_PROMPT = """You are an evaluation judge. Score the agent's answer against the expected answer on 4 dimensions.

User query: {query}
Expected answer: {expected}
Actual answer: {actual}

Score each dimension from 0.0 to 1.0:
- retrieval_hit: Did the answer use relevant information? (1.0=fully relevant, 0.0=completely off)
- faithfulness: Is the answer faithful to the expected content? (1.0=fully faithful, 0.0=contradicts)
- hallucination: Does the answer contain fabricated information? (1.0=no hallucination, 0.0=entirely fabricated)
- task_completion: Does the answer fully address the query? (1.0=complete, 0.0=no attempt)

Output ONLY a JSON object:
{{"retrieval_hit": 0.0, "faithfulness": 0.0, "hallucination": 0.0, "task_completion": 0.0}}"""

PASS_THRESHOLD = 0.6


async def score_sample(
    sample: GoldenSample,
    actual_answer: str,
    elapsed_ms: int = 0,
) -> EvalResult:
    llm = get_llm()

    prompt = SCORER_PROMPT.format(
        query=sample.query,
        expected=sample.expected_answer,
        actual=actual_answer,
    )

    resp = await llm.ainvoke([
        SystemMessage(content=prompt),
        HumanMessage(content="Score the answer now."),
    ])

    import json
    try:
        raw = resp.content.strip().removeprefix("```json").removesuffix("```").strip()
        scores = json.loads(raw)
        # Clamp to [0, 1]
        scores = {k: max(0.0, min(1.0, float(v))) for k, v in scores.items()}
    except (json.JSONDecodeError, AttributeError):
        scores = {"retrieval_hit": 0.0, "faithfulness": 0.0, "hallucination": 0.0, "task_completion": 0.0}

    avg_score = sum(scores.values()) / len(scores) if scores else 0.0

    return EvalResult(
        sample_id=sample.id,
        domain=sample.domain,
        actual_answer=actual_answer,
        scores=scores,
        passed=avg_score >= PASS_THRESHOLD,
        elapsed_ms=elapsed_ms,
    )


async def score_batch(
    samples_and_answers: list[tuple[GoldenSample, str]],
) -> list[EvalResult]:
    results = []
    for sample, answer in samples_and_answers:
        result = await score_sample(sample, answer)
        results.append(result)
        logger.info(
            "Scored %s: passed=%s avg=%.2f",
            sample.id, result.passed, sum(result.scores.values()) / 4,
        )
    return results

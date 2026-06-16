import json
import pathlib
from dataclasses import asdict
from datetime import datetime

from evaluation.golden_sample import EvalResult

REPORT_DIR = pathlib.Path("data/eval_reports")


def generate_report(
    results: list[EvalResult],
    run_name: str = "",
) -> dict:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if not run_name:
        run_name = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Overall scores
    all_scores = {}
    for dim in ("retrieval_hit", "faithfulness", "hallucination", "task_completion"):
        vals = [r.scores.get(dim, 0.0) for r in results]
        all_scores[dim] = round(sum(vals) / len(vals), 4) if vals else 0.0

    overall = round(sum(all_scores.values()) / len(all_scores), 4) if all_scores else 0.0

    # Per-domain breakdown
    domains: dict[str, list[EvalResult]] = {}
    for r in results:
        domains.setdefault(r.domain, []).append(r)

    domain_summary = {}
    for domain, domain_results in domains.items():
        dims = {}
        for dim in ("retrieval_hit", "faithfulness", "hallucination", "task_completion"):
            vals = [r.scores.get(dim, 0.0) for r in domain_results]
            dims[dim] = round(sum(vals) / len(vals), 4)
        domain_summary[domain] = {
            "count": len(domain_results),
            "pass_rate": round(sum(1 for r in domain_results if r.passed) / len(domain_results), 4),
            "scores": dims,
        }

    # Bad cases (failed samples)
    bad_cases = [
        {
            "sample_id": r.sample_id,
            "domain": r.domain,
            "scores": r.scores,
            "actual_answer": r.actual_answer[:500],
        }
        for r in results
        if not r.passed
    ]

    report = {
        "run_name": run_name,
        "timestamp": datetime.now().isoformat(),
        "total_samples": len(results),
        "passed": sum(1 for r in results if r.passed),
        "pass_rate": round(sum(1 for r in results if r.passed) / len(results), 4) if results else 0.0,
        "overall_score": overall,
        "dimension_scores": all_scores,
        "domain_summary": domain_summary,
        "bad_cases": bad_cases,
    }

    # Save report
    report_path = REPORT_DIR / f"{run_name}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    return report


def load_report(run_name: str) -> dict | None:
    path = REPORT_DIR / f"{run_name}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_reports() -> list[str]:
    return sorted([f.stem for f in REPORT_DIR.glob("*.json")], reverse=True)


def compare_runs(run_names: list[str]) -> dict:
    comparison = {}
    for name in run_names:
        report = load_report(name)
        if report:
            comparison[name] = {
                "pass_rate": report["pass_rate"],
                "overall_score": report["overall_score"],
                "dimension_scores": report["dimension_scores"],
                "total_samples": report["total_samples"],
            }
    return comparison

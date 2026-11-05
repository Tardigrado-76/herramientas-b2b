"""
Metrics Collector and Aggregator for Aegis-Harness.
"""

from typing import List, Dict
from datetime import datetime, timezone
from aegis.models import TestResult, SuiteSummary, TestCategory

class MetricsAggregator:
    """Aggregates individual test results into comprehensive metrics and category scores."""
    
    @staticmethod
    def aggregate(suite_name: str, results: List[TestResult], quality_gate_passed: bool = True) -> SuiteSummary:
        total = len(results)
        if total == 0:
            return SuiteSummary(
                suite_name=suite_name,
                timestamp=datetime.now(timezone.utc).isoformat(),
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                pass_rate_percent=0.0,
                overall_score=0.0,
                category_scores={},
                average_latency_ms=0.0,
                quality_gate_passed=False,
                results=[]
            )

        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        pass_rate = (passed / total) * 100.0

        overall_score = sum(r.overall_score for r in results) / total
        avg_latency = sum(r.execution_output.latency_ms for r in results) / total

        # Category scores
        cat_map: Dict[str, List[float]] = {}
        for r in results:
            cat_key = r.category.value
            cat_map.setdefault(cat_key, []).append(r.overall_score)

        category_scores = {
            cat: round(sum(scores) / len(scores), 2)
            for cat, scores in cat_map.items()
        }

        return SuiteSummary(
            suite_name=suite_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_tests=total,
            passed_tests=passed,
            failed_tests=failed,
            pass_rate_percent=round(pass_rate, 2),
            overall_score=round(overall_score, 2),
            category_scores=category_scores,
            average_latency_ms=round(avg_latency, 2),
            quality_gate_passed=quality_gate_passed,
            results=results
        )

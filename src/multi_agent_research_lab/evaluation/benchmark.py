"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and cost for a runner."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    
    # Calculate estimated cost from trace events
    total_cost = 0.0
    for event in state.trace:
        payload = event.get("payload", {})
        cost = payload.get("cost_usd")
        if isinstance(cost, (int, float)):
            total_cost += float(cost)
    
    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=total_cost if total_cost > 0 else None,
        quality_score=None,  # Can be added with external evaluation
    )
    
    return state, metrics

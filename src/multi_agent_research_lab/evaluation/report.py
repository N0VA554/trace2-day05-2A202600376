"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown with analysis."""

    lines = [
        "# Benchmark Report",
        "",
        "## Summary",
        "",
        "This report compares single-agent and multi-agent systems for research tasks.",
        "",
        "## Metrics Comparison",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality | Notes |",
        "|---|---:|---:|---:|---|",
    ]
    
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}/10"
        lines.append(
            f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} | {item.notes} |"
        )
    
    lines.extend([
        "",
        "## Analysis",
        "",
        "### Latency",
        "",
    ])
    
    if len(metrics) >= 2:
        baseline = metrics[0]
        multi_agent = metrics[1]
        if baseline.latency_seconds > 0:
            speedup = baseline.latency_seconds / multi_agent.latency_seconds
            lines.append(
                f"- Multi-agent latency: {speedup:.2f}x {'faster' if speedup > 1 else 'slower'} "
                f"than baseline"
            )
    
    lines.extend([
        "",
        "### Cost",
        "",
    ])
    
    if len(metrics) >= 2:
        total_cost_baseline = metrics[0].estimated_cost_usd or 0
        total_cost_multi = metrics[1].estimated_cost_usd or 0
        if total_cost_baseline > 0:
            cost_ratio = total_cost_multi / total_cost_baseline
            lines.append(
                f"- Multi-agent cost: {cost_ratio:.2f}x baseline cost"
            )
    
    lines.extend([
        "",
        "## Recommendations",
        "",
        "- Use single-agent for simple, direct queries with clear answers",
        "- Use multi-agent for complex research tasks requiring multiple perspectives",
        "- Consider latency vs. quality trade-offs for your use case",
        "",
    ])
    
    return "\n".join(lines)

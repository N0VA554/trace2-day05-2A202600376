"""Command-line entrypoint for the lab starter."""

import logging
from pathlib import Path
from typing import Annotated

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.services.llm_client import LLMClient

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()
logger = logging.getLogger(__name__)


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a single-agent baseline that directly answers the query."""

    _init()
    
    logger.info(f"Starting baseline (single-agent) for query: {query}")
    
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    
    # Use the baseline runner
    def baseline_runner(q: str) -> ResearchState:
        return _run_baseline_agent(q)
    
    try:
        result_state, metrics = run_benchmark("Single-Agent Baseline", query, baseline_runner)
        
        # Display results
        console.print(Panel.fit(
            result_state.final_answer or "No answer generated",
            title="Single-Agent Baseline Result"
        ))
        
        # Display metrics
        table = Table(title="Baseline Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Latency (s)", f"{metrics.latency_seconds:.2f}")
        if metrics.estimated_cost_usd:
            table.add_row("Est. Cost (USD)", f"${metrics.estimated_cost_usd:.4f}")
        console.print(table)
        
    except Exception as e:
        console.print(Panel.fit(str(e), title="Error", style="red"))
        raise typer.Exit(code=1) from e


def _run_baseline_agent(query: str) -> ResearchState:
    """Run a single-agent baseline that answers the query directly."""
    
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    
    llm_client = LLMClient()
    
    system_prompt = """You are a helpful research assistant. Answer the user's query 
comprehensively and accurately. Provide a well-structured response with relevant details 
and examples where appropriate. Target audience: technical learners."""
    
    user_prompt = f"""Please provide a comprehensive answer to the following query:

Query: {query}

Write a detailed response (aim for 500-800 words) that covers the main aspects of this topic."""
    
    response = llm_client.complete(system_prompt, user_prompt)
    state.final_answer = response.content
    
    # Record metrics in state
    state.add_trace_event("baseline_complete", {
        "input_tokens": response.input_tokens,
        "output_tokens": response.output_tokens,
        "cost_usd": response.cost_usd,
    })
    
    return state


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow."""

    _init()
    
    logger.info(f"Starting multi-agent workflow for query: {query}")
    
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    workflow = MultiAgentWorkflow()
    
    try:
        def multi_agent_runner(q: str) -> ResearchState:
            req = ResearchQuery(query=q)
            s = ResearchState(request=req)
            return workflow.run(s)
        
        result_state, metrics = run_benchmark("Multi-Agent System", query, multi_agent_runner)
        
        # Display results
        console.print(Panel.fit(
            result_state.final_answer or "No answer generated",
            title="Multi-Agent System Result"
        ))
        
        # Display routing history
        console.print(Panel(
            f"Route History: {' -> '.join(result_state.route_history)}",
            title="Execution Flow"
        ))
        
        # Display metrics
        table = Table(title="Multi-Agent Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Latency (s)", f"{metrics.latency_seconds:.2f}")
        if metrics.estimated_cost_usd:
            table.add_row("Est. Cost (USD)", f"${metrics.estimated_cost_usd:.4f}")
        table.add_row("Iterations", str(result_state.iteration))
        console.print(table)
        
    except Exception as e:
        console.print(Panel.fit(f"Error: {str(e)}", title="Error", style="red"))
        logger.exception("Multi-agent workflow failed")
        raise typer.Exit(code=1) from e


@app.command()
def benchmark(
    query: Annotated[str | None, typer.Option("--query", "-q", help="Single research query")] = None,
    queries_file: Annotated[
        Path | None, typer.Option("--queries-file", help="YAML file containing a list of queries")
    ] = None,
    out: Annotated[
        Path, typer.Option("--out", help="Output markdown report path")
    ] = Path("reports/benchmark_report.md"),
) -> None:
    """Run both baseline and multi-agent, then compare."""

    _init()

    if query is None and queries_file is None:
        raise typer.BadParameter("Provide either --query or --queries-file")
    
    try:
        queries: list[str] = []
        if queries_file is not None:
            logger.info(f"Loading benchmark queries from {queries_file}")
            data = yaml.safe_load(queries_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                queries = [str(x) for x in data]
            elif isinstance(data, dict) and isinstance(data.get("queries"), list):
                queries = [str(x) for x in data["queries"]]
            else:
                raise ValueError("Invalid queries file format. Expected list or {queries: [...]}.")
        else:
            queries = [query or ""]

        all_metrics = []
        for q in queries:
            logger.info(f"Starting benchmark for query: {q}")

            # Run baseline
            _baseline_state, baseline_metrics = run_benchmark(
                "Single-Agent Baseline",
                q,
                _run_baseline_agent,
            )

            # Run multi-agent
            def multi_agent_runner(q2: str) -> ResearchState:
                req = ResearchQuery(query=q2)
                s = ResearchState(request=req)
                workflow = MultiAgentWorkflow()
                return workflow.run(s)

            _multi_agent_state, multi_agent_metrics = run_benchmark(
                "Multi-Agent System",
                q,
                multi_agent_runner,
            )

            all_metrics.extend([baseline_metrics, multi_agent_metrics])

            # Display comparison per query
            comparison_table = Table(title=f"Benchmark Comparison: {q[:60]}")
            comparison_table.add_column("Metric", style="cyan")
            comparison_table.add_column("Baseline", style="green")
            comparison_table.add_column("Multi-Agent", style="blue")

            comparison_table.add_row(
                "Latency (s)",
                f"{baseline_metrics.latency_seconds:.2f}",
                f"{multi_agent_metrics.latency_seconds:.2f}",
            )

            if multi_agent_metrics.latency_seconds > 0:
                speedup = baseline_metrics.latency_seconds / multi_agent_metrics.latency_seconds
                comparison_table.add_row("Speedup", "1.0x", f"{speedup:.2f}x")

            console.print(comparison_table)

        # Generate and save report
        report = render_markdown_report(all_metrics)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")

        console.print(Panel.fit(
            f"Benchmark report saved to {out}",
            title="Success",
            style="green"
        ))
        
    except Exception as e:
        console.print(Panel.fit(str(e), title="Error", style="red"))
        logger.exception("Benchmark failed")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()

"""Analyst agent skeleton."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self) -> None:
        self.llm_client: LLMClient | None = None

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        
        with trace_span("analyst.run", {"has_research_notes": bool(state.research_notes)}) as span:
            logger.info("AnalystAgent starting")

            if not state.research_notes:
                logger.warning("No research notes found, skipping analysis")
                state.analysis_notes = "No research notes to analyze."
                state.add_trace_event("analyst_complete", {"skipped": True, "span": span})
                return state

            system_prompt = """You are a critical analyst. Your job is to:
1. Extract key claims and concepts from research notes
2. Identify any conflicting viewpoints
3. Flag weak evidence or unsupported claims
4. Highlight the most important findings

Provide your analysis in a structured format."""
        
            user_prompt = f"""Query: {state.request.query}

Research Notes:
{state.research_notes}

Please analyze these research notes and provide:
- Key claims and concepts
- Conflicting viewpoints (if any)
- Weak evidence or gaps
- Most important findings"""
        
            if self.llm_client is None:
                self.llm_client = LLMClient()
            response = self.llm_client.complete(system_prompt, user_prompt)
            state.analysis_notes = response.content

            state.add_trace_event("analyst_complete", {
                "analysis_notes_length": len(response.content),
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd,
                "span": span,
            })

            logger.info("AnalystAgent completed")

            return state

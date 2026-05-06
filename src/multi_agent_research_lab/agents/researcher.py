"""Researcher agent skeleton."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient

logger = logging.getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self) -> None:
        self.llm_client: LLMClient | None = None
        self.search_client = SearchClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        
        with trace_span("researcher.run", {"query": state.request.query}) as span:
            logger.info(f"ResearcherAgent starting for query: {state.request.query}")
        
            # Search for sources
            sources = self.search_client.search(
                state.request.query,
                max_results=state.request.max_sources,
            )
            state.sources = sources
        
            # Create research notes by synthesizing sources
            sources_text = "\n".join(
                [
                    f"- {s.title} ({s.url}): {s.snippet}"
                    for s in sources
                ]
            )
        
            system_prompt = """You are a research analyst. Your job is to read sources and create 
concise, well-organized research notes that capture key facts and concepts relevant to the query."""
        
            user_prompt = f"""Query: {state.request.query}

Sources:
{sources_text}

Create concise research notes (max 500 words) that synthesize these sources."""
        
            if self.llm_client is None:
                self.llm_client = LLMClient()
            response = self.llm_client.complete(system_prompt, user_prompt)
            state.research_notes = response.content
        
            state.add_trace_event("researcher_complete", {
                "sources_count": len(sources),
                "research_notes_length": len(response.content),
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd,
                "span": span,
            })
        
            logger.info(f"ResearcherAgent completed. Found {len(sources)} sources.")
        
            return state

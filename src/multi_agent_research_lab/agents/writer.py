"""Writer agent skeleton."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self) -> None:
        self.llm_client: LLMClient | None = None

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        
        with trace_span("writer.run", {"audience": state.request.audience}) as span:
            logger.info("WriterAgent starting")

            # Prepare context
            research_context = state.research_notes or "No research notes available."
            analysis_context = state.analysis_notes or "No analysis available."

            system_prompt = """You are an expert technical writer. Your job is to:
1. Synthesize research findings and analysis into a clear, comprehensive response
2. Write in a logical, well-structured format
3. Include citations or source references where appropriate
4. Target audience: {audience}
5. Keep response clear and actionable""".format(audience=state.request.audience)
        
            user_prompt = f"""Query: {state.request.query}

Research Notes:
{research_context}

Analysis:
{analysis_context}

Please write a comprehensive response (aim for 500-800 words) that synthesizes the research 
and analysis into a clear answer for the query. Structure your response logically and include 
relevant citations or source references."""
        
            if self.llm_client is None:
                self.llm_client = LLMClient()
            response = self.llm_client.complete(system_prompt, user_prompt)
            state.final_answer = response.content

            state.add_trace_event("writer_complete", {
                "final_answer_length": len(response.content),
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd,
                "span": span,
            })

            logger.info("WriterAgent completed")

            return state

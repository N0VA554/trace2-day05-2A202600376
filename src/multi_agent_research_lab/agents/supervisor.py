"""Supervisor / router skeleton."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def __init__(self) -> None:
        self.settings = get_settings()

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        
        with trace_span("supervisor.run", {"iteration": state.iteration}) as span:
            logger.info(f"SupervisorAgent routing decision (iteration {state.iteration})")
        
            # Check max iterations
            if state.iteration >= self.settings.max_iterations:
                logger.info("Max iterations reached, routing to done")
                state.record_route("done")
                state.add_trace_event("supervisor_complete", {"route": "done", "span": span})
                return state
        
            # Simple routing logic:
            # 1. First iteration -> researcher
            # 2. If research_notes exist and no analysis -> analyst
            # 3. If analysis exists and no final_answer -> writer
            # 4. Otherwise -> done
        
            if state.iteration == 0:
                # First iteration: always start with researcher
                logger.info("First iteration, routing to researcher")
                state.record_route("researcher")
                state.add_trace_event("supervisor_complete", {"route": "researcher", "span": span})
                return state
        
            if state.research_notes and not state.analysis_notes:
                # Have research but no analysis yet
                logger.info("Research notes exist, routing to analyst")
                state.record_route("analyst")
                state.add_trace_event("supervisor_complete", {"route": "analyst", "span": span})
                return state
        
            if state.research_notes and state.analysis_notes and not state.final_answer:
                # Have research and analysis but no final answer
                logger.info("Analysis exists, routing to writer")
                state.record_route("writer")
                state.add_trace_event("supervisor_complete", {"route": "writer", "span": span})
                return state
        
            # All done
            logger.info("All work completed, routing to done")
            state.record_route("done")
            state.add_trace_event("supervisor_complete", {"route": "done", "span": span})
            return state

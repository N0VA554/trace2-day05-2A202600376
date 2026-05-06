"""LangGraph workflow skeleton."""

import logging
from typing import Literal

from pydantic import TypeAdapter

from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.core.state import ResearchState

logger = logging.getLogger(__name__)


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(self) -> None:
        self.supervisor = SupervisorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.graph = self.build()

    def build(self) -> object:
        """Create a LangGraph graph."""
        try:
            from langgraph.graph import StateGraph  # type: ignore
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "LangGraph is not installed. Install optional deps with: pip install -e '.[llm]'"
            ) from e

        # Define the state graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes for each agent
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("researcher", self._researcher_node)
        workflow.add_node("analyst", self._analyst_node)
        workflow.add_node("writer", self._writer_node)
        workflow.add_node("done", self._done_node)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add conditional edges from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self._route_decision,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "writer": "writer",
                "done": "done",
            },
        )
        
        # Each worker routes back to supervisor for next decision
        workflow.add_edge("researcher", "supervisor")
        workflow.add_edge("analyst", "supervisor")
        workflow.add_edge("writer", "supervisor")
        
        # Done is terminal
        workflow.set_finish_point("done")
        
        logger.info("LangGraph workflow built successfully")
        return workflow.compile()

    def _supervisor_node(self, state: ResearchState) -> ResearchState:
        """Supervisor node: decides routing."""
        return self.supervisor.run(state)

    def _researcher_node(self, state: ResearchState) -> ResearchState:
        """Researcher node: searches and creates notes."""
        return self.researcher.run(state)

    def _analyst_node(self, state: ResearchState) -> ResearchState:
        """Analyst node: analyzes research."""
        return self.analyst.run(state)

    def _writer_node(self, state: ResearchState) -> ResearchState:
        """Writer node: creates final answer."""
        return self.writer.run(state)

    def _done_node(self, state: ResearchState) -> ResearchState:
        """Done node: terminal state."""
        logger.info("Workflow completed")
        return state

    def _route_decision(self, state: ResearchState) -> Literal["researcher", "analyst", "writer", "done"]:
        """Determine next route based on state."""
        # The route is already recorded by supervisor in state.route_history
        # Return the last recorded route
        if state.route_history:
            last_route = state.route_history[-1]
            if last_route in ["researcher", "analyst", "writer", "done"]:
                return last_route  # type: ignore
        return "done"

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        
        logger.info(f"Starting multi-agent workflow for query: {state.request.query}")
        
        # Invoke the graph
        result = self.graph.invoke(state)
        
        # Convert back to ResearchState if needed
        if isinstance(result, dict):
            state_adapter = TypeAdapter(ResearchState)
            result_state = state_adapter.validate_python(result)
        else:
            result_state = result
        
        logger.info(f"Workflow completed. Route history: {result_state.route_history}")
        
        return result_state

import pytest

from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState


def test_supervisor_routes_correctly() -> None:
    """Test that supervisor makes proper routing decisions."""
    
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    supervisor = SupervisorAgent()
    
    # First iteration should route to researcher
    result = supervisor.run(state)
    assert result.route_history[-1] == "researcher"
    
    # After researcher, should route to analyst
    result.research_notes = "Some research notes"
    result = supervisor.run(result)
    assert result.route_history[-1] == "analyst"
    
    # After analyst, should route to writer
    result.analysis_notes = "Some analysis"
    result = supervisor.run(result)
    assert result.route_history[-1] == "writer"
    
    # After writer, should route to done
    result.final_answer = "Final answer"
    result = supervisor.run(result)
    assert result.route_history[-1] == "done"

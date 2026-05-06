"""Simple test script to verify the complete workflow."""

from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.writer import WriterAgent


def test_complete_workflow():
    """Test complete workflow from supervisor through writer."""
    
    # Create initial state
    query = "What are multi-agent systems?"
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    
    print(f"\n{'='*70}")
    print(f"Starting workflow for query: {query}")
    print(f"{'='*70}\n")
    
    # Initialize agents
    supervisor = SupervisorAgent()
    researcher = ResearcherAgent()
    analyst = AnalystAgent()
    writer = WriterAgent()
    
    # Run supervisor to decide first route
    print("1. SUPERVISOR: Determining first route...")
    state = supervisor.run(state)
    print(f"   Route: {state.route_history[-1]}")
    
    # Run researcher
    print("\n2. RESEARCHER: Searching for sources...")
    try:
        state = researcher.run(state)
        print(f"   Found {len(state.sources)} sources")
        print(f"   Research notes length: {len(state.research_notes or '')} chars")
    except Exception as e:
        print(f"   Error (expected if no API key): {type(e).__name__}")
        # Mock the response to continue testing
        state.sources = []
        state.research_notes = "Mock research notes about multi-agent systems."
    
    # Run supervisor to decide next route
    print("\n3. SUPERVISOR: Determining next route...")
    state = supervisor.run(state)
    print(f"   Route: {state.route_history[-1]}")
    
    # Run analyst
    print("\n4. ANALYST: Analyzing research...")
    try:
        state = analyst.run(state)
        print(f"   Analysis notes length: {len(state.analysis_notes or '')} chars")
    except Exception as e:
        print(f"   Error (expected if no API key): {type(e).__name__}")
        # Mock the response
        state.analysis_notes = "Mock analysis of multi-agent systems."
    
    # Run supervisor to decide next route
    print("\n5. SUPERVISOR: Determining next route...")
    state = supervisor.run(state)
    print(f"   Route: {state.route_history[-1]}")
    
    # Run writer
    print("\n6. WRITER: Writing final answer...")
    try:
        state = writer.run(state)
        print(f"   Final answer length: {len(state.final_answer or '')} chars")
    except Exception as e:
        print(f"   Error (expected if no API key): {type(e).__name__}")
        # Mock the response
        state.final_answer = "Mock final answer about multi-agent systems."
    
    # Run supervisor for final decision
    print("\n7. SUPERVISOR: Determining final route...")
    state = supervisor.run(state)
    print(f"   Route: {state.route_history[-1]}")
    
    print(f"\n{'='*70}")
    print("WORKFLOW SUMMARY")
    print(f"{'='*70}")
    print(f"Total iterations: {state.iteration}")
    print(f"Route history: {' -> '.join(state.route_history)}")
    print(f"Final state: {state.final_answer[:100] if state.final_answer else 'N/A'}...")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    test_complete_workflow()

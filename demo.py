#!/usr/bin/env python3
"""
Demo script showing the complete multi-agent research system.
This demonstrates the workflow without requiring real API keys.
"""

from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.schemas import SourceDocument
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.writer import WriterAgent


def demo_workflow():
    """Demonstrate the complete multi-agent workflow with mock responses."""

    print("Multi-Agent Research System Demo")
    print("=" * 50)

    # Create initial state
    query = "Explain the concept of multi-agent systems in AI"
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)

    print(f"Query: {query}")
    print()

    # Initialize agents
    supervisor = SupervisorAgent()
    researcher = ResearcherAgent()
    analyst = AnalystAgent()
    writer = WriterAgent()

    # Step 1: Supervisor routes to researcher
    print("1. SUPERVISOR: Starting workflow")
    state = supervisor.run(state)
    print(f"   -> Route: {state.route_history[-1]}")
    print()

    # Step 2: Researcher searches and creates notes
    print("2. RESEARCHER: Gathering information")
    # Mock the research phase since we don't have API keys
    state.sources = [
        SourceDocument(
            title="Multi-Agent Systems Overview",
            url="https://example.com/multi-agent",
            snippet="Multi-agent systems consist of multiple autonomous agents that interact to solve problems.",
            metadata={"source": "demo"},
        ),
        SourceDocument(
            title="AI Agent Coordination",
            url="https://example.com/coordination",
            snippet="Agents coordinate through communication protocols and shared goals.",
            metadata={"source": "demo"},
        ),
    ]
    state.research_notes = """
    Multi-agent systems (MAS) are computational systems where multiple autonomous agents interact to achieve goals.

    Key characteristics:
    - Autonomy: Each agent operates independently
    - Interaction: Agents communicate and coordinate
    - Cooperation: Agents work together toward common objectives
    - Decentralization: No single point of control

    Applications include robotics, game AI, traffic management, and distributed problem-solving.
    """
    print(f"   -> Found {len(state.sources)} sources")
    print(f"   -> Created research notes ({len(state.research_notes)} chars)")
    print()

    # Step 3: Supervisor routes to analyst
    print("3. SUPERVISOR: Next step")
    state = supervisor.run(state)
    print(f"   -> Route: {state.route_history[-1]}")
    print()

    # Step 4: Analyst analyzes the research
    print("4. ANALYST: Analyzing findings")
    state.analysis_notes = """
    Analysis of multi-agent systems research:

    Strengths:
    - Scalability: Can handle complex problems through division of labor
    - Robustness: System continues functioning if individual agents fail
    - Flexibility: Agents can adapt to changing environments

    Key concepts identified:
    - Agent autonomy and decision-making
    - Communication protocols (ACL, FIPA)
    - Coordination mechanisms (auctions, contracts, voting)
    - Emergent behavior from simple agent interactions

    Potential challenges:
    - Coordination overhead
    - Conflicting agent goals
    - Communication bottlenecks
    """
    print(f"   -> Created analysis ({len(state.analysis_notes)} chars)")
    print()

    # Step 5: Supervisor routes to writer
    print("5. SUPERVISOR: Final step")
    state = supervisor.run(state)
    print(f"   -> Route: {state.route_history[-1]}")
    print()

    # Step 6: Writer creates final answer
    print("6. WRITER: Synthesizing final response")
    state.final_answer = """
    # Multi-Agent Systems in AI

    Multi-agent systems (MAS) represent a paradigm in artificial intelligence where multiple autonomous agents interact and collaborate to solve complex problems that would be difficult or impossible for a single agent to handle effectively.

    ## Core Concepts

    **Autonomy**: Each agent in a MAS operates independently, making its own decisions based on local information and goals.

    **Interaction**: Agents communicate through various protocols to share information, negotiate, and coordinate actions.

    **Cooperation**: Agents work together toward shared objectives, often through division of labor and specialization.

    ## Key Advantages

    1. **Scalability**: Complex problems can be decomposed into smaller, manageable tasks
    2. **Robustness**: The system remains functional even if individual agents fail
    3. **Flexibility**: Agents can adapt to dynamic environments and changing requirements

    ## Applications

    - **Robotics**: Swarm robotics for exploration and task completion
    - **Traffic Management**: Coordinating autonomous vehicles
    - **Game AI**: Non-player characters that interact realistically
    - **Distributed Problem Solving**: Breaking down complex optimization problems

    ## Challenges

    - Coordination overhead and communication costs
    - Potential conflicts between agent goals
    - Ensuring system-wide coherence and stability

    Multi-agent systems represent a powerful approach to tackling complex, distributed problems in AI, with applications across numerous domains.
    """
    print(f"   -> Created final answer ({len(state.final_answer)} chars)")
    print()

    # Step 7: Supervisor completes workflow
    print("7. SUPERVISOR: Workflow complete")
    state = supervisor.run(state)
    print(f"   -> Route: {state.route_history[-1]}")
    print()

    # Summary
    print("WORKFLOW SUMMARY")
    print("=" * 50)
    print(f"Total iterations: {state.iteration}")
    print(f"Route history: {' -> '.join(state.route_history)}")
    print(f"Final answer preview: {state.final_answer[:200]}...")
    print()
    print("Multi-agent research system completed successfully!")
    print("To run with real APIs, add OPENAI_API_KEY to .env file")


if __name__ == "__main__":
    demo_workflow()

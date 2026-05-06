"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings.

        Minimal implementation:
        - If there is no final answer, do nothing.
        - If there are sources, check whether the final answer references at least one source URL.
        - Append a short "Critic Notes" section to `state.analysis_notes` (non-destructive).
        """

        if not state.final_answer:
            return state

        urls = [s.url for s in state.sources if s.url]
        has_any_url = any((u and u in state.final_answer) for u in urls)

        notes_lines: list[str] = ["Critic Notes:"]
        if urls:
            if has_any_url:
                notes_lines.append("- Citation check: at least one source URL is referenced.")
            else:
                notes_lines.append(
                    "- Citation check: no source URLs referenced. Consider adding a Sources section."
                )
        else:
            notes_lines.append("- Citation check: no sources were collected in this run.")

        critic_notes = "\n".join(notes_lines)

        if state.analysis_notes:
            state.analysis_notes = f"{state.analysis_notes}\n\n{critic_notes}"
        else:
            state.analysis_notes = critic_notes

        state.add_trace_event("critic_complete", {"has_any_url_citation": has_any_url, "sources": len(urls)})
        return state

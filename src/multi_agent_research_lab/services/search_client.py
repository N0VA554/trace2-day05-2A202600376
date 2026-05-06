"""Search client abstraction for ResearcherAgent."""

import logging
from typing import Any

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import SourceDocument

logger = logging.getLogger(__name__)


class SearchClient:
    """Provider-agnostic search client with mock and Tavily support."""

    def __init__(self) -> None:
        self.settings = get_settings()
        # Try to import Tavily if available
        try:
            from tavily import TavilyClient
            
            if self.settings.tavily_api_key:
                self.tavily_client = TavilyClient(api_key=self.settings.tavily_api_key)
                self.use_tavily = True
            else:
                self.use_tavily = False
                logger.info("Tavily API key not provided, using mock search")
        except ImportError:
            self.use_tavily = False
            logger.info("Tavily not installed, using mock search")

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query.
        
        Falls back to mock search if Tavily is not available or not configured.
        """
        
        if self.use_tavily:
            return self._search_tavily(query, max_results)
        else:
            return self._search_mock(query, max_results)

    def _search_tavily(self, query: str, max_results: int) -> list[SourceDocument]:
        """Search using Tavily API."""
        try:
            response = self.tavily_client.search(query=query, max_results=max_results)
            
            documents = []
            for result in response.get("results", []):
                doc = SourceDocument(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    snippet=result.get("content", "")[:500],  # Truncate to 500 chars
                    metadata={"source": "tavily"},
                )
                documents.append(doc)
            
            logger.info(f"Found {len(documents)} results from Tavily for query: {query}")
            return documents
        except Exception as e:
            logger.error(f"Tavily search failed: {e}, falling back to mock search")
            return self._search_mock(query, max_results)

    def _search_mock(self, query: str, max_results: int) -> list[SourceDocument]:
        """Mock search for development and testing."""
        # Mock relevant results based on common query patterns
        mock_sources: dict[str, list[dict[str, str]]] = {
            "default": [
                {
                    "title": "Overview of Topic",
                    "url": "https://example.com/overview",
                    "snippet": f"This is a comprehensive overview of {query}. Lorem ipsum dolor sit amet.",
                },
                {
                    "title": "Best Practices",
                    "url": "https://example.com/practices",
                    "snippet": f"Key best practices for {query} implementation and usage.",
                },
                {
                    "title": "Technical Deep Dive",
                    "url": "https://example.com/technical",
                    "snippet": f"Technical analysis and architecture considerations for {query}.",
                },
                {
                    "title": "Comparison and Analysis",
                    "url": "https://example.com/comparison",
                    "snippet": f"Comparison of different approaches to {query}.",
                },
                {
                    "title": "Recent Updates",
                    "url": "https://example.com/updates",
                    "snippet": f"Latest developments and updates in {query} space.",
                },
            ]
        }
        
        sources = mock_sources.get("default", mock_sources["default"])[:max_results]
        
        documents = [
            SourceDocument(
                title=s["title"],
                url=s["url"],
                snippet=s["snippet"],
                metadata={"source": "mock"},
            )
            for s in sources
        ]
        
        logger.info(f"Returning {len(documents)} mock results for query: {query}")
        return documents

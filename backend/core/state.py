"""
LangGraph state definition for the Football Intelligence System.
Shared state typed dictionary across all agents.
"""

import operator
from typing import TypedDict, Annotated, Optional
from langchain_core.messages import AnyMessage


class FootballState(TypedDict):
    """State shared across all agents in the LangGraph pipeline."""

    messages: Annotated[list[AnyMessage], operator.add]

    user_query: str

    player_results: str
    web_results: str
    standings_results: Optional[str]

    analysis: str
    recommendations: str

    final_response: str
    sources_used: list[str]

    llm_calls: int

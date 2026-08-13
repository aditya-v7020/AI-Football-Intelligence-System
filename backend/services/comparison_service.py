"""
Comparison service — runs two player lookups via multi-source pipeline + AI comparison summary.
"""

import uuid
from langchain_core.messages import HumanMessage

from backend.core.graph import get_app
from backend.core.tools.multi_source_pipeline import get_multi_source_player_data
from backend.models.schemas import PlayerData, ComparisonResponse
from backend.config import settings


async def compare_players(player1: str, player2: str) -> ComparisonResponse:
    """
    Compare two players using multi-source API data + LangGraph AI analysis.
    """
    season = settings.FOOTBALL_SEASON

    # Get structured data & text for both players
    p1_text, p1_raw, s1 = get_multi_source_player_data(player1, season)
    p2_text, p2_raw, s2 = get_multi_source_player_data(player2, season)

    p1_data = [PlayerData(**p) for p in p1_raw]
    p2_data = [PlayerData(**p) for p in p2_raw]

    combined_sources = list(set(s1 + s2))

    comparison_query = (
        f"Compare football players {player1} and {player2}.\n"
        f"PLAYER 1 DATA:\n{p1_text}\n\n"
        f"PLAYER 2 DATA:\n{p2_text}\n\n"
        f"Provide a detailed side-by-side comparison including "
        f"strengths, weaknesses, playing style, statistics, "
        f"and which player is better in key areas. Attribute statistics to their data source."
    )

    thread_id = f"compare_{uuid.uuid4().hex[:12]}"
    config = {"configurable": {"thread_id": thread_id}}

    app = get_app()

    try:
        result = app.invoke(
            {
                "messages": [HumanMessage(content=comparison_query)],
                "user_query": comparison_query,
                "player_results": f"{p1_text}\n\n{p2_text}",
                "web_results": "",
                "standings_results": None,
                "analysis": "",
                "recommendations": "",
                "final_response": "",
                "sources_used": combined_sources,
                "llm_calls": 0,
            },
            config=config,
        )

        ai_comparison = result.get("final_response", "")
        all_sources = list(set(result.get("sources_used", []) + combined_sources))

    except Exception as e:
        ai_comparison = f"AI comparison could not be generated: {str(e)}"
        all_sources = combined_sources

    return ComparisonResponse(
        player1_data=p1_data,
        player2_data=p2_data,
        ai_comparison=ai_comparison,
        sources=all_sources,
        thread_id=thread_id,
    )

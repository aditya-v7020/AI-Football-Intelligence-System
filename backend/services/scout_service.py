"""
Scout service — Advanced AI scouting using real retrieved multi-source candidate data.
"""

import uuid
import re
from langchain_core.messages import HumanMessage

from backend.core.graph import get_app
from backend.core.tools.multi_source_pipeline import get_real_scout_candidates, get_multi_source_player_data
from backend.models.schemas import ScoutResponse, PlayerData


def _extract_reference_player_and_position(req: str) -> tuple[str, str]:
    """Extract reference player name or target position from scouting query."""
    player_match = re.search(r"similar to ([A-Za-z\s]+)", req, re.IGNORECASE)
    ref_name = player_match.group(1).strip() if player_match else None

    pos = "Midfielder"
    for p_name in ["Winger", "Striker", "Forward", "Midfielder", "Defender", "Goalkeeper"]:
        if p_name.lower() in req.lower():
            pos = p_name
            break

    return ref_name, pos


async def run_scout(requirements: str, thread_id: str | None = None) -> ScoutResponse:
    """
    Run AI scouting:
    1. Fetch real candidate players & statistics from available APIs (No hallucinated stats).
    2. Rank candidates and pass real data into LangGraph multi-agent pipeline.
    """
    if not thread_id:
        thread_id = f"scout_{uuid.uuid4().hex[:12]}"

    ref_player, target_pos = _extract_reference_player_and_position(requirements)

    # Fetch real candidate players from multi-source APIs
    candidates_raw, scout_sources = get_real_scout_candidates(position=target_pos, reference_player_name=ref_player)
    candidate_models = [PlayerData(**c) for c in candidates_raw]

    # Format real candidate data for LLM prompt
    candidates_formatted = []
    for idx, c in enumerate(candidates_raw, 1):
        candidates_formatted.append(
            f"{idx}. {c['name']} ({c['team']}, {c['league']}) - Pos: {c['position']} | Age: {c['age']} | "
            f"Goals: {c['goals']} | Assists: {c['assists']} | Rating: {c['rating']} | [Source: {c['source']}]"
        )
    candidates_prompt_text = "\n".join(candidates_formatted) if candidates_formatted else "No candidate players retrieved from APIs."

    scout_query = f"""
AI Scouting Task:
REQUIREMENTS: {requirements}

REAL CANDIDATE PLAYERS RETRIEVED FROM FOOTBALL APIS:
{candidates_prompt_text}

Instructions for Scouting Report:
1. Compare and rank the real candidate players listed above based strictly on their retrieved metrics.
2. Explain why each player fits the user's requirements.
3. Do not invent players, transfers, or statistics not present in the candidate data.
4. Mark missing statistics as 'Not available'.
"""

    config = {"configurable": {"thread_id": thread_id}}
    app = get_app()

    try:
        result = app.invoke(
            {
                "messages": [HumanMessage(content=scout_query)],
                "user_query": scout_query,
                "player_results": candidates_prompt_text,
                "web_results": "",
                "standings_results": None,
                "analysis": "",
                "recommendations": "",
                "final_response": "",
                "sources_used": scout_sources,
                "llm_calls": 0,
            },
            config=config,
        )

        all_sources = list(set(result.get("sources_used", []) + scout_sources))

        return ScoutResponse(
            requirements=requirements,
            report=result.get("final_response", "No scouting report generated."),
            player_data=candidates_prompt_text,
            candidates=candidate_models,
            sources=all_sources,
            web_research=result.get("web_results"),
            thread_id=thread_id,
        )

    except Exception as e:
        return ScoutResponse(
            requirements=requirements,
            report=f"Scouting error: {str(e)}",
            candidates=candidate_models,
            sources=scout_sources,
            thread_id=thread_id,
        )

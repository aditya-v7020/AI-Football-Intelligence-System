"""
LangGraph agent functions for the Football Intelligence System.
Enhanced multi-agent pipeline with multi-source data collection, source attribution,
and zero-hallucination guarantees.
"""

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_groq import ChatGroq

from backend.config import settings
from backend.core.state import FootballState
from backend.core.tools.multi_source_pipeline import (
    get_multi_source_player_data,
    get_multi_source_competition_data,
)
from backend.core.tools.tavily_tool import tavily_search


def _get_llm() -> ChatGroq:
    """Create LLM instance from configuration."""
    return ChatGroq(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=settings.LLM_TEMPERATURE,
    )


# =========================================================
# PLAYER DATA AGENT
# =========================================================

def player_agent(state: FootballState) -> dict:
    """
    Retrieves structured player data from API-Football, Sportmonks, and TheSportsDB.
    """
    query = state["user_query"]
    sources_used = list(state.get("sources_used", []))

    try:
        player_text, _, p_sources = get_multi_source_player_data(query)
        sources_used.extend(p_sources)

        if not player_text:
            player_text = "No structured player data found across APIs."

    except Exception as error:
        player_text = f"Unable to retrieve player data: {str(error)}"

    return {
        "player_results": player_text,
        "sources_used": list(set(sources_used)),
        "messages": [
            AIMessage(content="Multi-source player data retrieval completed.")
        ],
    }


# =========================================================
# WEB & COMPETITION RESEARCH AGENT
# =========================================================

def research_agent(state: FootballState) -> dict:
    """
    Searches for standings, fixtures via Football-Data.org and web info via Tavily.
    """
    user_q = state["user_query"]
    sources_used = list(state.get("sources_used", []))

    # 1. Competition/Standings research if relevant
    standings_text, comp_sources = get_multi_source_competition_data(user_q)
    sources_used.extend(comp_sources)

    # 2. Web research via Tavily
    raw_query = f"Football info, stats, news, transfers for: {user_q}"
    search_query = raw_query[:350]

    try:
        web_data = tavily_search(search_query)
        if web_data and "No web search" not in web_data:
            sources_used.append("Tavily Web Search")
        else:
            web_data = "No additional web research found."

    except Exception as error:
        web_data = f"Unable to retrieve web research: {str(error)}"

    combined_research = web_data
    if standings_text:
        combined_research = f"{standings_text}\n\n{web_data}"

    return {
        "web_results": combined_research,
        "standings_results": standings_text,
        "sources_used": list(set(sources_used)),
        "messages": [
            AIMessage(content="Football web & competition research completed.")
        ],
    }


# =========================================================
# FOOTBALL ANALYSIS AGENT
# =========================================================

def analysis_agent(state: FootballState) -> dict:
    """
    Analyzes collected multi-source data using LLM with strict source attribution.
    """
    sources_str = ", ".join(state.get("sources_used", [])) or "API Data & Web Research"

    prompt = f"""
You are analyzing a football-related user request.

USER QUERY:
{state['user_query']}

STRUCTURED PLAYER DATA (API-Football / Sportmonks / TheSportsDB):
{state['player_results']}

COMPETITION & WEB RESEARCH (Football-Data.org / Tavily):
{state['web_results']}

Analyze the available information carefully.

Requirements:
- Do not invent statistics or facts.
- If reliable statistics or data are unavailable, explicitly write 'Not available' or 'N/A'.
- Include source attributions clearly e.g. [Source: API-Football], [Source: Football-Data.org], [Source: Tavily Web Search].
- Structure into relevant sections: Player Profile, Performance & Statistics, Tactical Assessment, Overall Summary.
"""

    llm = _get_llm()

    try:
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are an expert football analyst and scout. "
                        "Never fabricate statistics. Always attribute data to its source."
                    )
                ),
                HumanMessage(content=prompt),
            ]
        )

        return {
            "analysis": response.content,
            "messages": [response],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    except Exception as error:
        return {
            "analysis": f"Football analysis could not be generated: {str(error)}",
            "messages": [AIMessage(content="Football analysis failed.")],
            "llm_calls": state.get("llm_calls", 0),
        }


# =========================================================
# FINAL RESPONSE AGENT
# =========================================================

def final_agent(state: FootballState) -> dict:
    """
    Generates the final user-facing response with source attributions.
    """
    sources_list = state.get("sources_used", [])
    sources_formatted = ", ".join(sources_list) if sources_list else "API-Football, Tavily Web Search"

    final_prompt = f"""
Generate the final answer to the user's football question.

USER QUERY:
{state['user_query']}

MULTI-SOURCE PLAYER DATA:
{state['player_results']}

COMPETITION & WEB RESEARCH:
{state['web_results']}

FOOTBALL ANALYSIS:
{state['analysis']}

DATA SOURCES QUERIED:
{sources_formatted}

Create a professional and clear final response.

Requirements:
1. Answer the user's actual question directly.
2. Rely strictly on retrieved data. Never invent statistics or transfers.
3. Mark missing stats as 'Not available' or 'N/A'.
4. Include explicit source attributions e.g. [Source: API-Football], [Source: Football-Data.org], [Source: Tavily Web Search].
5. End with a list of Data Sources used.
"""

    llm = _get_llm()

    try:
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are the final response agent of a multi-source football AI intelligence system. "
                        "Combine the supplied information into an accurate and well-structured answer with markdown formatting. "
                        "Always include source attributions for data."
                    )
                ),
                HumanMessage(content=final_prompt),
            ]
        )

        return {
            "final_response": response.content,
            "messages": [response],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    except Exception as error:
        error_message = f"Unable to generate final response: {str(error)}"

        return {
            "final_response": error_message,
            "messages": [AIMessage(content=error_message)],
            "llm_calls": state.get("llm_calls", 0),
        }

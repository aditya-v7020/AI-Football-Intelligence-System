import os
import operator
from typing import TypedDict, Annotated

import psycopg
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

from langchain_groq import ChatGroq

from tools.tavily_tool import tavily_search
from tools.football_tool import search_players


# =========================================================
# 1. LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")


required_variables = {
    "GROQ_API_KEY": GROQ_API_KEY,
    "TAVILY_API_KEY": TAVILY_API_KEY,
    "FOOTBALL_API_KEY": FOOTBALL_API_KEY,
    "DATABASE_URL": DATABASE_URL,
}

missing_variables = [
    name
    for name, value in required_variables.items()
    if not value
]

if missing_variables:
    raise ValueError(
        "Missing environment variables: "
        + ", ".join(missing_variables)
    )


# =========================================================
# 2. INITIALIZE LLM
# =========================================================

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0.2,
)


# =========================================================
# 3. LANGGRAPH STATE
# =========================================================

class FootballState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

    user_query: str

    player_results: str
    web_results: str

    analysis: str
    recommendations: str

    final_response: str

    llm_calls: int


# =========================================================
# 4. PLAYER DATA AGENT
# =========================================================

def player_agent(state: FootballState):

    query = state["user_query"]

    try:
        player_data = search_players(query)

        if not player_data:
            player_data = "No player data was found from API-Football."

    except Exception as error:
        player_data = (
            f"Unable to retrieve player data: {str(error)}"
        )

    return {
        "player_results": player_data,

        "messages": [
            AIMessage(
                content="Football player data retrieval completed."
            )
        ],
    }


# =========================================================
# 5. WEB RESEARCH AGENT
# =========================================================

def research_agent(state: FootballState):

    search_query = (
        "Latest reliable football information, statistics, "
        "recent performances, club information, injuries, "
        "transfers and news about: "
        f"{state['user_query']}"
    )

    try:
        web_data = tavily_search(search_query)

        if not web_data:
            web_data = "No additional web information was found."

    except Exception as error:
        web_data = (
            f"Unable to retrieve web research: {str(error)}"
        )

    return {
        "web_results": web_data,

        "messages": [
            AIMessage(
                content="Football web research completed."
            )
        ],
    }


# =========================================================
# 6. FOOTBALL ANALYSIS AGENT
# =========================================================

def analysis_agent(state: FootballState):

    prompt = f"""
You are analyzing a football-related user request.

USER QUERY:
{state['user_query']}

API-FOOTBALL DATA:
{state['player_results']}

CURRENT WEB RESEARCH:
{state['web_results']}

Analyze the available information carefully.

Your analysis should include relevant sections such as:

- Player profile
- Current club
- Position
- Age and nationality
- Recent performance
- Important statistics
- Goals and assists
- Strengths
- Weaknesses
- Playing style
- Tactical characteristics
- Overall assessment

Only include sections that are relevant to the user's question.

Do not invent statistics or facts.

If information is unavailable, clearly state that it is unavailable.

Distinguish factual information from your own football analysis.
"""

    try:
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are an expert football analyst, "
                        "scout and data analyst. Use the supplied "
                        "data carefully and never fabricate "
                        "football statistics."
                    )
                ),

                HumanMessage(content=prompt),
            ]
        )

        analysis = response.content

        return {
            "analysis": analysis,

            "messages": [response],

            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    except Exception as error:

        return {
            "analysis": (
                f"Football analysis could not be generated: {str(error)}"
            ),

            "messages": [
                AIMessage(
                    content="Football analysis failed."
                )
            ],

            "llm_calls": state.get("llm_calls", 0),
        }


# =========================================================
# 7. FINAL RESPONSE AGENT
# =========================================================

def final_agent(state: FootballState):

    final_prompt = f"""
Generate the final answer to the user's football question.

USER QUERY:
{state['user_query']}

API-FOOTBALL DATA:
{state['player_results']}

WEB RESEARCH:
{state['web_results']}

FOOTBALL ANALYSIS:
{state['analysis']}

Create a professional and easy-to-understand final response.

Requirements:

1. Answer the user's actual question directly.
2. Use API-Football data when available.
3. Use recent web research when relevant.
4. Use the football analysis provided above.
5. Do not invent statistics, clubs, transfers or achievements.
6. Clearly indicate when reliable information is unavailable.
7. Avoid repeating the same information.
8. Use headings and bullet points when they improve readability.
9. Finish with a concise overall assessment or recommendation.

If the user asks for a player recommendation, explain why the
recommended player is suitable.
"""

    try:
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are the final response agent of a "
                        "multi-agent football intelligence system. "
                        "Combine the supplied information into an "
                        "accurate and useful answer."
                    )
                ),

                HumanMessage(
                    content=final_prompt
                ),
            ]
        )

        return {
            "final_response": response.content,

            "messages": [response],

            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    except Exception as error:

        error_message = (
            f"Unable to generate final response: {str(error)}"
        )

        return {
            "final_response": error_message,

            "messages": [
                AIMessage(content=error_message)
            ],

            "llm_calls": state.get("llm_calls", 0),
        }


# =========================================================
# 8. CREATE LANGGRAPH
# =========================================================

graph = StateGraph(FootballState)


# Add agents/nodes
graph.add_node(
    "player_agent",
    player_agent
)

graph.add_node(
    "research_agent",
    research_agent
)

graph.add_node(
    "analysis_agent",
    analysis_agent
)

graph.add_node(
    "final_agent",
    final_agent
)


# =========================================================
# 9. CONNECT AGENTS
# =========================================================

graph.add_edge(
    START,
    "player_agent"
)

graph.add_edge(
    "player_agent",
    "research_agent"
)

graph.add_edge(
    "research_agent",
    "analysis_agent"
)

graph.add_edge(
    "analysis_agent",
    "final_agent"
)

graph.add_edge(
    "final_agent",
    END
)


# =========================================================
# 10. POSTGRESQL MEMORY
# =========================================================

try:
    print("\nConnecting to PostgreSQL...")

    _conn = psycopg.connect(
        DATABASE_URL,
        autocommit=True,
        prepare_threshold=0,
        connect_timeout=10,
    )

    print("PostgreSQL connected successfully.")

    checkpointer = PostgresSaver(_conn)

    checkpointer.setup()

    print("LangGraph PostgreSQL memory ready.\n")

except psycopg.OperationalError as error:

    print("\nPostgreSQL connection failed.")
    print(f"Reason: {error}")

    print(
        "\nCheck DATABASE_URL in your .env file. "
        "PostgreSQL should be running on port 5432."
    )

    raise


# =========================================================
# 11. COMPILE LANGGRAPH
# =========================================================

app = graph.compile(
    checkpointer=checkpointer
)


# =========================================================
# 12. RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print("\n======================================")
    print("   AI FOOTBALL INTELLIGENCE SYSTEM")
    print("======================================\n")

    config = {
        "configurable": {
            "thread_id": "football_user_1"
        }
    }

    user_input = input(
        "Enter football player or analysis request: "
    ).strip()

    if not user_input:
        print("\nPlease enter a football-related question.")

    else:

        try:

            result = app.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content=user_input
                        )
                    ],

                    "user_query": user_input,

                    "player_results": "",

                    "web_results": "",

                    "analysis": "",

                    "recommendations": "",

                    "final_response": "",

                    "llm_calls": 0,
                },

                config=config,
            )

            print("\n")
            print("=" * 60)
            print("FINAL RESPONSE")
            print("=" * 60)
            print()

            print(
                result.get(
                    "final_response",
                    "No final response generated."
                )
            )

            print()
            print("=" * 60)

            print(
                f"LLM calls: "
                f"{result.get('llm_calls', 0)}"
            )

            print("=" * 60)

        except Exception as error:

            print("\nApplication error:")
            print(error)
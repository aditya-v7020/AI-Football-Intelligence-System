"""
LangGraph graph construction and PostgreSQL checkpointer.
Extracted from the original main.py — graph topology preserved exactly.

Graph flow:
  START → player_agent → research_agent → analysis_agent → final_agent → END
"""

import psycopg
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import MemorySaver

from backend.config import settings
from backend.core.state import FootballState
from backend.core.agents import (
    player_agent,
    research_agent,
    analysis_agent,
    final_agent,
)


# Module-level references managed by init/shutdown lifecycle
_db_connection = None
_checkpointer = None
_compiled_app = None


def init_graph():
    """
    Initialize the LangGraph graph with PostgreSQL checkpointer.
    Called once during FastAPI startup.
    """
    global _db_connection, _checkpointer, _compiled_app

    # --- Build the graph (same topology as original main.py) ---
    graph = StateGraph(FootballState)

    graph.add_node("player_agent", player_agent)
    graph.add_node("research_agent", research_agent)
    graph.add_node("analysis_agent", analysis_agent)
    graph.add_node("final_agent", final_agent)

    graph.add_edge(START, "player_agent")
    graph.add_edge("player_agent", "research_agent")
    graph.add_edge("research_agent", "analysis_agent")
    graph.add_edge("analysis_agent", "final_agent")
    graph.add_edge("final_agent", END)

    # --- Connect PostgreSQL checkpointer ---
    if settings.DATABASE_URL:
        try:
            print("\nConnecting to PostgreSQL...")

            _db_connection = psycopg.connect(
                settings.DATABASE_URL,
                autocommit=True,
                prepare_threshold=0,
                connect_timeout=2,
            )


            print("PostgreSQL connected successfully.")

            _checkpointer = PostgresSaver(_db_connection)
            _checkpointer.setup()

            print("LangGraph PostgreSQL memory ready.\n")

        except Exception as error:
            print(f"\nPostgreSQL connection failed: {error}")
            print("Falling back to MemorySaver in-memory checkpointing.")
            _db_connection = None
            _checkpointer = MemorySaver()
    else:
        print("\nNo DATABASE_URL configured. Using MemorySaver in-memory checkpointing.")
        _checkpointer = MemorySaver()

    # --- Compile ---
    _compiled_app = graph.compile(
        checkpointer=_checkpointer
    )

    return _compiled_app



def get_app():
    """Return the compiled LangGraph application."""
    global _compiled_app
    if _compiled_app is None:
        init_graph()
    return _compiled_app


def shutdown_graph():
    """Clean up database connection on shutdown."""
    global _db_connection
    if _db_connection is not None:
        try:
            _db_connection.close()
            print("PostgreSQL connection closed.")
        except Exception:
            pass


def check_db_health() -> bool:
    """Check if the PostgreSQL connection is alive."""
    global _db_connection
    if _db_connection is None:
        return False
    try:
        _db_connection.execute("SELECT 1")
        return True
    except Exception:
        return False

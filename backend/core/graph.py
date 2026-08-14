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
_db_error = None


def get_db_error() -> str:
    """Return the last database connection error message if any."""
    global _db_error
    return _db_error or ""


def get_db_url() -> str:
    """Return normalized PostgreSQL URL (converts postgres:// to postgresql://)."""
    url = (settings.DATABASE_URL or "").strip()
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def connect_db() -> bool:
    """Establish or re-establish PostgreSQL connection and PostgresSaver checkpointer."""
    global _db_connection, _checkpointer, _db_error
    url = get_db_url()
    if not url:
        _db_connection = None
        _checkpointer = MemorySaver()
        _db_error = "DATABASE_URL environment variable is not configured"
        return False

    if _db_connection is not None:
        try:
            _db_connection.close()
        except Exception:
            pass
        _db_connection = None

    is_local = "localhost" in url or "127.0.0.1" in url
    ssl_options = ["disable", "prefer"] if is_local else ["require", "prefer", "disable"]

    last_error = None
    for sslmode in ssl_options:
        try:
            print(f"\nConnecting to PostgreSQL (sslmode={sslmode})...")
            kwargs = {"autocommit": True, "prepare_threshold": 0, "connect_timeout": 10}
            if "sslmode=" not in url:
                kwargs["sslmode"] = sslmode

            _db_connection = psycopg.connect(url, **kwargs)
            print(f"PostgreSQL connected successfully (sslmode={sslmode}).")

            _checkpointer = PostgresSaver(_db_connection)
            _checkpointer.setup()
            print("LangGraph PostgreSQL memory ready.\n")
            _db_error = None
            return True

        except Exception as error:
            last_error = error
            _db_connection = None
            continue

    _db_error = str(last_error) if last_error else "Unknown connection failure"
    print(f"\nPostgreSQL connection failed: {_db_error}")
    print("Falling back to MemorySaver in-memory checkpointing.")
    _checkpointer = MemorySaver()
    return False


def build_graph():
    """Build the uncompiled StateGraph topology."""
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
    return graph


def init_graph():
    """
    Initialize the LangGraph graph with PostgreSQL checkpointer.
    Called once during FastAPI startup.
    """
    global _db_connection, _checkpointer, _compiled_app

    graph = build_graph()
    connect_db()
    _compiled_app = graph.compile(checkpointer=_checkpointer)
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
        _db_connection = None


def check_db_health() -> bool:
    """Check if PostgreSQL connection is alive, attempting auto-reconnect if down."""
    global _db_connection, _checkpointer, _compiled_app
    url = get_db_url()
    if not url:
        return False

    if _db_connection is not None:
        try:
            _db_connection.execute("SELECT 1")
            return True
        except Exception as error:
            print(f"PostgreSQL connection ping failed ({error}). Attempting reconnect...")
            _db_connection = None

    # Connection is None or dead, attempt reconnect
    reconnected = connect_db()
    if reconnected and _checkpointer is not None:
        try:
            graph = build_graph()
            _compiled_app = graph.compile(checkpointer=_checkpointer)
        except Exception as err:
            print(f"Graph recompile error: {err}")
    return reconnected

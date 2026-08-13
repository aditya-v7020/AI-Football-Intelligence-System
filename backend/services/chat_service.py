"""
Chat service — orchestrates LangGraph invocation for chat queries.
Provides both standard execution and real-time SSE event streaming for progress tracking.
"""

import json
import uuid
from typing import AsyncGenerator
from langchain_core.messages import HumanMessage

from backend.core.graph import get_app
from backend.models.schemas import ChatResponse, AgentStep


async def process_chat(query: str, thread_id: str | None = None) -> ChatResponse:
    """
    Run a user query through the full LangGraph agent pipeline.
    Returns structured response with agent execution steps and source attributions.
    """
    if not thread_id:
        thread_id = f"thread_{uuid.uuid4().hex[:12]}"

    config = {"configurable": {"thread_id": thread_id}}
    app = get_app()

    agent_names = ["player_agent", "research_agent", "analysis_agent", "final_agent"]
    agents = [AgentStep(agent=name, status="pending") for name in agent_names]

    try:
        result = app.invoke(
            {
                "messages": [HumanMessage(content=query)],
                "user_query": query,
                "player_results": "",
                "web_results": "",
                "standings_results": None,
                "analysis": "",
                "recommendations": "",
                "final_response": "",
                "sources_used": [],
                "llm_calls": 0,
            },
            config=config,
        )

        for a in agents:
            a.status = "completed"

        sources = result.get("sources_used", [])

        return ChatResponse(
            thread_id=thread_id,
            query=query,
            final_response=result.get("final_response", "No response generated."),
            player_data=result.get("player_results"),
            web_research=result.get("web_results"),
            analysis=result.get("analysis"),
            sources=sources,
            llm_calls=result.get("llm_calls", 0),
            agents=agents,
        )

    except Exception as e:
        for a in agents:
            if a.status != "completed":
                a.status = "failed"
                a.message = str(e)

        return ChatResponse(
            thread_id=thread_id,
            query=query,
            final_response=f"Error processing your request: {str(e)}",
            agents=agents,
        )


async def process_chat_stream(query: str, thread_id: str | None = None) -> AsyncGenerator[str, None]:
    """
    Async generator that streams real-time LangGraph agent execution progress via Server-Sent Events (SSE).
    Sends live node transition updates as each agent completes its work.
    """
    if not thread_id:
        thread_id = f"thread_{uuid.uuid4().hex[:12]}"

    config = {"configurable": {"thread_id": thread_id}}
    app = get_app()

    agent_names = ["player_agent", "research_agent", "analysis_agent", "final_agent"]

    initial_input = {
        "messages": [HumanMessage(content=query)],
        "user_query": query,
        "player_results": "",
        "web_results": "",
        "standings_results": None,
        "analysis": "",
        "recommendations": "",
        "final_response": "",
        "sources_used": [],
        "llm_calls": 0,
    }

    # Initial start event
    start_payload = {
        "event": "start",
        "thread_id": thread_id,
        "agents": [{"agent": name, "status": "pending"} for name in agent_names],
    }
    yield f"data: {json.dumps(start_payload)}\n\n"

    # First agent running event
    yield f"data: {json.dumps({'event': 'agent_start', 'agent': 'player_agent', 'thread_id': thread_id})}\n\n"

    accumulated_state = dict(initial_input)

    try:
        # Use LangGraph stream to receive node completion events as they happen
        for chunk in app.stream(initial_input, config=config):
            for node_name, node_output in chunk.items():
                if isinstance(node_output, dict):
                    accumulated_state.update(node_output)

                if node_name in agent_names:
                    # Notify frontend that this node completed
                    yield f"data: {json.dumps({'event': 'agent_completed', 'agent': node_name, 'thread_id': thread_id})}\n\n"

                    # Notify next node running if available
                    curr_idx = agent_names.index(node_name)
                    if curr_idx + 1 < len(agent_names):
                        next_agent = agent_names[curr_idx + 1]
                        yield f"data: {json.dumps({'event': 'agent_start', 'agent': next_agent, 'thread_id': thread_id})}\n\n"

        # Final completion payload
        final_resp = accumulated_state.get("final_response") or "No final response generated."
        sources = list(set(accumulated_state.get("sources_used", [])))

        finish_payload = {
            "event": "finish",
            "thread_id": thread_id,
            "final_response": final_resp,
            "sources": sources,
            "player_results": accumulated_state.get("player_results"),
            "web_results": accumulated_state.get("web_results"),
            "analysis": accumulated_state.get("analysis"),
            "llm_calls": accumulated_state.get("llm_calls", 0),
        }
        yield f"data: {json.dumps(finish_payload)}\n\n"

    except Exception as e:
        err_payload = {
            "event": "error",
            "thread_id": thread_id,
            "error": str(e),
        }
        yield f"data: {json.dumps(err_payload)}\n\n"


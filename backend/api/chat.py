"""
Chat API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from backend.models.schemas import ChatRequest, ChatResponse
from backend.services.chat_service import process_chat, process_chat_stream

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a football question to the multi-agent AI system.
    Returns the final response along with intermediate agent data.
    """
    query = request.query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if len(query) > 2000:
        raise HTTPException(status_code=400, detail="Query is too long (max 2000 characters).")

    try:
        response = await process_chat(query, request.thread_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.post("/stream")
async def chat_stream_post(request: ChatRequest):
    """
    Stream real-time agent progress and final response via SSE (POST request).
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    if len(query) > 2000:
        raise HTTPException(status_code=400, detail="Query is too long (max 2000 characters).")

    return StreamingResponse(
        process_chat_stream(query, request.thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/stream")
async def chat_stream_get(
    q: str = Query(..., min_length=1, max_length=2000, description="Query text"),
    thread_id: str | None = Query(None, description="Optional thread ID")
):
    """
    Stream real-time agent progress and final response via SSE (GET request for EventSource).
    """
    query = q.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    return StreamingResponse(
        process_chat_stream(query, thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


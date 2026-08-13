"""
FastAPI application server for the AI Football Intelligence System.
"""

import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure the project root is on sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from backend.core.graph import init_graph, shutdown_graph
from backend.api.chat import router as chat_router
from backend.api.players import router as players_router
from backend.api.scout import router as scout_router
from backend.api.recommend import router as recommend_router
from backend.api.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    # --- Startup ---
    missing = settings.validate()
    if missing:
        print(f"WARNING: Missing environment variables: {', '.join(missing)}")

    print("Initializing LangGraph pipeline...")
    init_graph()
    print("LangGraph pipeline ready.")

    yield

    # --- Shutdown ---
    print("Shutting down...")
    shutdown_graph()


app = FastAPI(
    title="AI Football Intelligence System",
    description=(
        "Multi-agent AI system for football analysis, "
        "player recommendations, scouting, and comparisons."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allows the Vite frontend and Vercel deployments to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount routers
app.include_router(chat_router)
app.include_router(players_router)
app.include_router(scout_router)
app.include_router(recommend_router)
app.include_router(health_router)



@app.get("/")
async def root():
    return {
        "name": "AI Football Intelligence System",
        "version": "1.0.0",
        "docs": "/docs",
    }

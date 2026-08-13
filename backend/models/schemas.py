"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any


# =========================================================
# Chat models
# =========================================================

class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""
    query: str = Field(
        ..., min_length=1, max_length=2000,
        description="The football-related question or request"
    )
    thread_id: Optional[str] = Field(
        None,
        description="Thread ID for conversation continuity. Auto-generated if not provided."
    )


class AgentStep(BaseModel):
    """Represents one agent's execution in the pipeline."""
    agent: str
    status: str  # "pending", "running", "completed", "failed"
    message: Optional[str] = None


class ChatResponse(BaseModel):
    """Response body for the chat endpoint."""
    thread_id: str
    query: str
    final_response: str
    player_data: Optional[str] = None
    web_research: Optional[str] = None
    analysis: Optional[str] = None
    sources: list[str] = []
    llm_calls: int = 0
    agents: list[AgentStep] = []


# =========================================================
# Player models
# =========================================================

class PlayerSearchRequest(BaseModel):
    """Request for player search."""
    pass


class PlayerData(BaseModel):
    """Structured player data normalized across multiple APIs."""
    id: Optional[Any] = None
    name: str = "Unknown"
    firstname: str = ""
    lastname: str = ""
    age: Optional[Any] = None
    nationality: str = "Not available"
    birth_date: Optional[str] = "Not available"
    height: Optional[str] = "Not available"
    weight: Optional[str] = "Not available"
    photo: str = ""
    position: str = "Not available"
    team: str = "Not available"
    team_logo: str = ""
    league: str = "Not available"
    league_logo: str = ""
    season: int = 2024
    appearances: int = 0
    minutes: int = 0
    rating: Optional[str] = "N/A"
    goals: int = 0
    assists: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    passes_accuracy: Optional[str] = "N/A"
    shots_total: int = 0
    shots_on_target: int = 0
    dribbles_success: int = 0
    tackles_total: int = 0
    source: str = "Multi-Source"


class PlayerSearchResponse(BaseModel):
    """Response for player search."""
    query: str
    season: int
    players: list[PlayerData] = []
    sources: list[str] = []
    total: int = 0


# =========================================================
# Comparison models
# =========================================================

class ComparisonRequest(BaseModel):
    """Request body for player comparison."""
    player1: str = Field(..., min_length=1, max_length=200)
    player2: str = Field(..., min_length=1, max_length=200)


class ComparisonResponse(BaseModel):
    """Response for player comparison."""
    player1_data: list[PlayerData] = []
    player2_data: list[PlayerData] = []
    ai_comparison: str = ""
    sources: list[str] = []
    thread_id: str = ""


# =========================================================
# Scout models
# =========================================================

class ScoutRequest(BaseModel):
    """Request body for AI scouting."""
    requirements: str = Field(
        ..., min_length=1, max_length=2000,
        description="Natural language scouting requirements"
    )
    thread_id: Optional[str] = None


class ScoutResponse(BaseModel):
    """Response for AI scouting."""
    requirements: str
    report: str
    player_data: Optional[str] = None
    candidates: list[PlayerData] = []
    sources: list[str] = []
    web_research: Optional[str] = None
    thread_id: str = ""


# =========================================================
# Recommendation models
# =========================================================

class RecommendationRequest(BaseModel):
    """Request for ML-powered player recommendations."""
    similar_to: Optional[str] = Field(None, description="Reference player name e.g. Haaland")
    position: Optional[str] = Field(None, description="Target position filter")
    max_age: Optional[int] = Field(None, description="Maximum age filter")
    top_k: int = Field(5, ge=1, le=20, description="Number of recommendations")
    method: str = Field("cosine", description="'cosine' or 'knn'")


class RecommendationItem(BaseModel):
    """Individual player recommendation with ML match metrics."""
    name: str
    team: str = "Not available"
    league: str = "Not available"
    position: str = "Not available"
    age: int = 0
    goals: int = 0
    assists: int = 0
    rating: str = "N/A"
    photo: str = ""
    similarity_score: float = 0.0
    similarity_percentage: str = "0.0%"
    explanation: str = ""
    source: str = "Multi-Source API"


class RecommendationResponse(BaseModel):
    """Response for ML player recommendations."""
    status: str
    reference_player: Optional[str] = None
    algorithm: str = "Content-based Cosine Similarity with Z-score feature scaling"
    total_candidates_evaluated: int = 0
    recommendations: list[RecommendationItem] = []
    sources: list[str] = []
    message: Optional[str] = None


# =========================================================
# Health models
# =========================================================

class HealthResponse(BaseModel):
    """Health check response for all system integrations."""
    status: str
    database: str
    groq_configured: bool
    tavily_configured: bool
    football_api_configured: bool
    sportmonks_configured: bool
    thesportsdb_configured: bool
    football_data_configured: bool
    football_season: int


"""
Player recommendation API endpoints powered by the ML recommendation engine.
"""

from fastapi import APIRouter, HTTPException
from backend.models.schemas import RecommendationRequest, RecommendationResponse
from backend.ml.recommender import PlayerRecommender

router = APIRouter(prefix="/api/recommend", tags=["Recommendation"])
recommender = PlayerRecommender()


@router.post("", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get ML-powered player recommendations based on feature similarity (Cosine Similarity or KNN).
    Uses real player data retrieved via multi-source football APIs.
    """
    criteria = {
        "similar_to": request.similar_to,
        "position": request.position,
        "max_age": request.max_age,
        "method": request.method,
    }

    try:
        res = recommender.recommend(criteria=criteria, top_k=request.top_k)
        if res.get("status") == "error":
            raise HTTPException(status_code=400, detail=res.get("message", "Recommendation failed."))
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation pipeline failed: {str(e)}")

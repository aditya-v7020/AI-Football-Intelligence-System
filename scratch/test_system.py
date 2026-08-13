"""
Verification script for AI Football Intelligence System.
Tests ML Preprocessor, Similarity engine (Cosine + KNN), Recommender, and FastAPI endpoints.
"""

import sys
import os

# Ensure backend is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ml.preprocessor import DataPreprocessor
from backend.ml.similarity import PlayerSimilarity
from backend.ml.recommender import PlayerRecommender
from backend.models.schemas import (
    RecommendationRequest,
    ChatRequest,
    ComparisonRequest,
    ScoutRequest,
)


def test_ml_pipeline():
    print("========================================")
    print("1. Testing ML Pipeline Components")
    print("========================================")

    sample_players = [
        {
            "id": 1,
            "name": "Erling Haaland",
            "team": "Manchester City",
            "league": "Premier League",
            "position": "Attacker",
            "age": 24,
            "goals": 27,
            "assists": 5,
            "minutes": 2550,
            "rating": "7.8",
            "passes_accuracy": "78%",
            "dribbles_success": 22,
            "tackles_total": 8,
            "shots_on_target": 55,
            "photo": "https://example.com/haaland.png",
        },
        {
            "id": 2,
            "name": "Kylian Mbappe",
            "team": "Real Madrid",
            "league": "La Liga",
            "position": "Attacker",
            "age": 25,
            "goals": 26,
            "assists": 7,
            "minutes": 2480,
            "rating": "7.9",
            "passes_accuracy": "82%",
            "dribbles_success": 45,
            "tackles_total": 12,
            "shots_on_target": 50,
            "photo": "https://example.com/mbappe.png",
        },
        {
            "id": 3,
            "name": "Harry Kane",
            "team": "Bayern Munich",
            "league": "Bundesliga",
            "position": "Attacker",
            "age": 31,
            "goals": 36,
            "assists": 8,
            "minutes": 2800,
            "rating": "8.0",
            "passes_accuracy": "80%",
            "dribbles_success": 18,
            "tackles_total": 15,
            "shots_on_target": 60,
            "photo": "https://example.com/kane.png",
        },
        {
            "id": 4,
            "name": "Jude Bellingham",
            "team": "Real Madrid",
            "league": "La Liga",
            "position": "Midfielder",
            "age": 21,
            "goals": 19,
            "assists": 6,
            "minutes": 2400,
            "rating": "7.7",
            "passes_accuracy": "88%",
            "dribbles_success": 35,
            "tackles_total": 30,
            "shots_on_target": 35,
            "photo": "https://example.com/bellingham.png",
        },
    ]

    # Preprocessor test
    prep = DataPreprocessor()
    df = prep.preprocess_player_dicts(sample_players)
    print(f"DataPreprocessor: Successfully processed {len(df)} players into feature matrix.")
    assert len(df) == 4, "DataFrame length mismatch"

    # Similarity engine test (Cosine)
    sim = PlayerSimilarity()
    fit_res = sim.fit(df, prep.FEATURE_COLUMNS)
    print(f"PlayerSimilarity Fit Result: {fit_res}")
    assert fit_res["status"] == "fitted", "Fitting failed"

    cosine_res = sim.find_similar("Erling Haaland", top_k=2, method="cosine")
    print("\nCosine Similarity Result for 'Erling Haaland':")
    print(cosine_res)
    assert cosine_res["status"] == "success", "Cosine similarity search failed"
    assert len(cosine_res["similar_players"]) > 0, "No recommendations returned"

    # Similarity engine test (KNN)
    knn_res = sim.find_similar("Erling Haaland", top_k=2, method="knn")
    print("\nKNN Similarity Result for 'Erling Haaland':")
    print(knn_res)
    assert knn_res["status"] == "success", "KNN similarity search failed"

    # Recommender test
    recommender = PlayerRecommender()
    rec_res = recommender.recommend({"similar_to": "Haaland", "method": "cosine"}, top_k=3)
    print("\nPlayerRecommender Result:")
    print(f"Status: {rec_res['status']}")
    print(f"Algorithm: {rec_res['algorithm']}")
    print(f"Total evaluated: {rec_res['total_candidates_evaluated']}")
    print(f"Recommendations count: {len(rec_res['recommendations'])}")

    print("\nML Pipeline verification PASSED cleanly!\n")


def test_fastapi_server_routes():
    print("========================================")
    print("2. Testing FastAPI Server & App Routes")
    print("========================================")

    from backend.server import app

    routes = []
    for r in app.routes:
        if hasattr(r, "path") and r.path:
            routes.append(r.path)
        if type(r).__name__ == "_IncludedRouter" and hasattr(r, "original_router"):
            for sub_r in r.original_router.routes:
                if hasattr(sub_r, "path"):
                    routes.append(sub_r.path)

    print(f"All registered route paths ({len(routes)}): {routes}")

    expected_paths = [
        "/",
        "/api/health",
        "/api/chat",
        "/api/chat/stream",
        "/api/players/search",
        "/api/players/news",
        "/api/players/compare",
        "/api/scout",
        "/api/recommend",
    ]

    for p in expected_paths:
        assert p in routes, f"Missing expected route: {p}"
        print(f"Verified registered endpoint: {p}")

    print("\nFastAPI Server route verification PASSED cleanly!\n")


if __name__ == "__main__":
    test_ml_pipeline()
    test_fastapi_server_routes()
    print("ALL TESTS PASSED SUCCESSFULLY!")





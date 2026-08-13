"""
Player recommendation engine.
Combines real multi-source API football data, preprocessing, Z-score feature scaling,
and Cosine Similarity / KNN to generate ML-driven player recommendations.
"""

from typing import Optional, Dict, List, Any


from backend.ml.preprocessor import DataPreprocessor
from backend.ml.similarity import PlayerSimilarity
from backend.core.tools.multi_source_pipeline import (
    get_multi_source_player_data,
    get_real_scout_candidates,
)


class PlayerRecommender:
    """
    Generates data-driven player recommendations using ML feature similarity.
    Operates on live multi-source API player metrics.
    """

    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.similarity = PlayerSimilarity()

    @property
    def ml_available(self) -> bool:
        """ML engine is ready for inference."""
        return True

    def recommend(
        self,
        criteria: Dict[str, Any],
        top_k: int = 5,
    ) -> Dict[str, Any]:

        """
        Recommend players based on criteria.

        Args:
            criteria: Dict with keys:
                - similar_to: Reference player name (e.g. "Haaland", "Bellingham")
                - position: Target position filter (optional)
                - max_age: Maximum age filter (optional)
                - method: "cosine" or "knn" (default "cosine")
            top_k: Number of recommendations to return

        Returns:
            Dict containing status, recommendations list, reference player, and explanations.
        """
        similar_to = criteria.get("similar_to", "").strip()
        position_filter = criteria.get("position")
        max_age = criteria.get("max_age")
        method = criteria.get("method", "cosine")

        if not similar_to and not position_filter:
            return {
                "status": "error",
                "message": "Please specify a reference player name ('similar_to') or target position.",
                "recommendations": [],
            }

        # 1. Fetch real player candidates from APIs for comparison
        raw_candidates, sources = get_real_scout_candidates(
            position=position_filter or "Midfielder",
            reference_player_name=similar_to if similar_to else None,
        )

        # Ensure the target reference player is included in the feature pool
        if similar_to:
            _, ref_players, ref_sources = get_multi_source_player_data(similar_to)
            if ref_players:
                # Put target player at the head of candidate list
                ref_p = ref_players[0]
                raw_candidates = [ref_p] + [
                    c for c in raw_candidates if c.get("name", "").lower() != ref_p.get("name", "").lower()
                ]
                sources = list(set(sources + ref_sources))

        if not raw_candidates:
            return {
                "status": "no_data",
                "message": "No player statistics could be retrieved from football APIs for evaluation.",
                "recommendations": [],
                "sources": sources,
            }

        # 2. Preprocess raw API metrics into scaled feature matrix
        df = self.preprocessor.preprocess_player_dicts(raw_candidates)

        # 3. Fit similarity engine on candidate feature matrix
        fit_result = self.similarity.fit(df, self.preprocessor.FEATURE_COLUMNS)

        if fit_result["status"] != "fitted":
            return {
                "status": "error",
                "message": f"Feature extraction failed: {fit_result.get('message')}",
                "recommendations": [],
                "sources": sources,
            }

        # 4. Perform Cosine Similarity / KNN search
        target_search_name = similar_to if similar_to else raw_candidates[0]["name"]
        sim_res = self.similarity.find_similar(
            player_name=target_search_name, top_k=top_k * 2, method=method
        )

        if sim_res["status"] != "success":
            return {
                "status": sim_res["status"],
                "message": sim_res.get("message", "Unable to compute player recommendations."),
                "recommendations": [],
                "sources": sources,
            }

        raw_recs = sim_res.get("similar_players", [])

        # 5. Apply user filters (max_age, position) safely
        filtered_recs = []
        for p in raw_recs:
            if max_age is not None and p.get("age", 0) > 0 and p.get("age", 0) > int(max_age):
                continue
            if position_filter:
                pos_str = str(p.get("position", "")).lower()
                req_pos = str(position_filter).lower()
                if req_pos not in pos_str and pos_str not in req_pos:
                    continue
            filtered_recs.append(p)
            if len(filtered_recs) >= top_k:
                break

        # Fallback to unfiltered recs if filtering left no candidates
        final_recs = filtered_recs if filtered_recs else raw_recs[:top_k]

        return {
            "status": "success",
            "reference_player": sim_res.get("reference_player", target_search_name),
            "algorithm": f"Content-based {method.upper()} with Z-score feature scaling",
            "total_candidates_evaluated": len(raw_candidates),
            "recommendations": final_recs,
            "sources": sources,
        }


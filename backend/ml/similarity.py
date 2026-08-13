"""
Player similarity engine using Cosine Similarity and K-Nearest Neighbors (KNN).
Provides mathematical similarity measurements over scaled numerical feature vectors.
"""

from typing import Optional, List, Dict, Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors


class PlayerSimilarity:
    """
    Finds similar players using mathematical similarity measures.
    Supports Cosine Similarity and K-Nearest Neighbors on scaled features.
    """

    def __init__(self):
        self._dataframe: Optional[pd.DataFrame] = None
        self._feature_matrix: Optional[np.ndarray] = None
        self._scaler: Optional[StandardScaler] = None
        self._feature_columns: List[str] = []
        self._player_names: List[str] = []
        self._is_fitted: bool = False

    @property
    def is_available(self) -> bool:
        """Return True if fitted on player data."""
        return self._is_fitted and self._feature_matrix is not None and len(self._player_names) > 0

    def fit(self, dataframe: pd.DataFrame, feature_columns: List[str]) -> Dict[str, Any]:

        """
        Fit the similarity model on a preprocessed DataFrame.
        Scales features using StandardScaler (z-score normalization).
        """
        if dataframe is None or dataframe.empty:
            self._is_fitted = False
            return {"status": "no_dataset", "message": "No dataset provided for fitting."}

        self._dataframe = dataframe.copy()
        self._feature_columns = [col for col in feature_columns if col in dataframe.columns]

        if not self._feature_columns:
            self._is_fitted = False
            return {"status": "no_features", "message": "No valid numerical feature columns found."}

        self._player_names = dataframe["name"].tolist()
        raw_features = dataframe[self._feature_columns].fillna(0.0).values

        # Scale features so variables with different units are comparable
        self._scaler = StandardScaler()
        self._feature_matrix = self._scaler.fit_transform(raw_features)
        self._is_fitted = True

        return {
            "status": "fitted",
            "players": len(self._player_names),
            "features": len(self._feature_columns),
        }

    def find_similar(
        self, player_name: str, top_k: int = 5, method: str = "cosine"
    ) -> dict:
        """
        Find the top-K most similar players to a given player.
        """
        if not self.is_available:
            return {
                "status": "not_fitted",
                "message": "Similarity model is not fitted on data.",
                "similar_players": [],
            }

        # Case-insensitive name match
        matched_idx = None
        target_name_lower = player_name.lower().strip()
        for idx, name in enumerate(self._player_names):
            if target_name_lower in name.lower() or name.lower() in target_name_lower:
                matched_idx = idx
                break

        if matched_idx is None:
            return {
                "status": "not_found",
                "message": f"Player '{player_name}' not found in current dataset pool.",
                "similar_players": [],
            }

        target_name = self._player_names[matched_idx]
        player_vector = self._feature_matrix[matched_idx].reshape(1, -1)
        target_row = self._dataframe.iloc[matched_idx]

        results = []

        if method == "knn" and len(self._player_names) > 1:
            n_neighbors = min(top_k + 1, len(self._player_names))
            knn = NearestNeighbors(n_neighbors=n_neighbors, metric="euclidean")
            knn.fit(self._feature_matrix)
            distances, indices = knn.kneighbors(player_vector)

            for idx, dist in zip(indices[0], distances[0]):
                if idx == matched_idx:
                    continue
                row = self._dataframe.iloc[idx]
                sim_score = max(0.0, round(float(1.0 / (1.0 + dist)), 4))
                results.append(self._format_similar_record(row, sim_score, target_row))

        else:  # Default to Cosine Similarity
            sim_scores = cosine_similarity(player_vector, self._feature_matrix)[0]
            top_indices = np.argsort(sim_scores)[::-1]

            for idx in top_indices:
                if idx == matched_idx:
                    continue
                row = self._dataframe.iloc[idx]
                score = round(float(sim_scores[idx]), 4)
                results.append(self._format_similar_record(row, score, target_row))
                if len(results) >= top_k:
                    break

        return {
            "status": "success",
            "reference_player": target_name,
            "method": method,
            "similar_players": results[:top_k],
        }

    def _format_similar_record(
        self, row: pd.Series, similarity_score: float, target_row: pd.Series
    ) -> dict:
        """Format player match record with explanation of similarity."""
        reasons = []
        if abs(row.get("goals_per_90", 0) - target_row.get("goals_per_90", 0)) < 0.25:
            reasons.append("Similar goals per 90 output")
        if abs(row.get("assists_per_90", 0) - target_row.get("assists_per_90", 0)) < 0.2:
            reasons.append("Similar playmaking & assists per 90")
        if str(row.get("position")).lower() == str(target_row.get("position")).lower():
            reasons.append(f"Identical position ({row.get('position')})")
        if abs(row.get("age_val", 25) - target_row.get("age_val", 25)) <= 3:
            reasons.append("Similar age profile")

        explanation = ", ".join(reasons) if reasons else "High overall metric vector correlation"

        return {
            "name": str(row.get("name")),
            "team": str(row.get("team")),
            "league": str(row.get("league")),
            "position": str(row.get("position")),
            "age": int(row.get("age_val", 0)),
            "goals": int(row.get("goals", 0)),
            "assists": int(row.get("assists", 0)),
            "rating": str(row.get("rating")),
            "photo": str(row.get("photo", "")),
            "similarity_score": float(similarity_score),
            "similarity_percentage": f"{round(similarity_score * 100, 1)}%",
            "explanation": explanation,
            "source": str(row.get("source", "Multi-Source API")),
        }


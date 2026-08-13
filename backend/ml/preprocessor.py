"""
Data preprocessing module for the ML player recommendation pipeline.
Extracts, cleans, and standardizes player feature vectors from API player data.
"""

import os
import numpy as np
import pandas as pd
from typing import Optional, List, Dict, Any



class DataPreprocessor:
    """
    Handles loading, cleaning, and feature engineering for player datasets.
    Can operate on player dataframes loaded from CSV or dynamic API player dicts.
    """

    DATASET_DIR = os.path.join(os.path.dirname(__file__), "data")

    # Primary numerical feature columns used for vector scaling and similarity
    FEATURE_COLUMNS = [
        "goals_per_90",
        "assists_per_90",
        "rating_val",
        "pass_acc_val",
        "dribbles_val",
        "tackles_val",
        "shots_target_val",
        "age_val",
    ]

    def __init__(self):
        self._dataframe: Optional[pd.DataFrame] = None
        self._is_loaded: bool = False

    @property
    def is_available(self) -> bool:
        """Check if a preprocessed dataset is loaded and non-empty."""
        return self._is_loaded and self._dataframe is not None and not self._dataframe.empty

    def preprocess_player_dicts(self, players: List[Dict[str, Any]]) -> pd.DataFrame:

        """
        Convert raw player dicts from API-Football/multi-source pipeline
        into a clean, feature-engineered Pandas DataFrame.
        """
        if not players:
            self._dataframe = pd.DataFrame()
            self._is_loaded = False
            return self._dataframe

        records = []
        for p in players:
            # Safely parse numeric fields
            minutes = self._safe_float(p.get("minutes"), default=0.0)
            mins_factor = 90.0 / minutes if minutes >= 90.0 else 1.0

            goals = self._safe_float(p.get("goals"), default=0.0)
            assists = self._safe_float(p.get("assists"), default=0.0)
            shots_target = self._safe_float(p.get("shots_on_target"), default=0.0)
            dribbles = self._safe_float(p.get("dribbles_success"), default=0.0)
            tackles = self._safe_float(p.get("tackles_total"), default=0.0)
            rating = self._safe_float(p.get("rating"), default=7.0)
            pass_acc = self._safe_float(p.get("passes_accuracy"), default=75.0)
            age = self._safe_float(p.get("age"), default=25.0)

            rec = {
                "id": str(p.get("id") or p.get("name")),
                "name": str(p.get("name", "Unknown Player")),
                "team": str(p.get("team", "Unknown Team")),
                "league": str(p.get("league", "Unknown League")),
                "position": str(p.get("position", "Midfielder")),
                "nationality": str(p.get("nationality", "Unknown")),
                "photo": str(p.get("photo", "")),
                "source": str(p.get("source", "Multi-Source API")),
                # Raw stats
                "goals": int(goals),
                "assists": int(assists),
                "minutes": int(minutes),
                "appearances": int(self._safe_float(p.get("appearances"), default=0.0)),
                "rating": rating,
                # Engineered Per-90 and Normalized Features
                "goals_per_90": round(goals * mins_factor, 2),
                "assists_per_90": round(assists * mins_factor, 2),
                "rating_val": round(rating, 2),
                "pass_acc_val": round(pass_acc, 2),
                "dribbles_val": round(dribbles * mins_factor, 2),
                "tackles_val": round(tackles * mins_factor, 2),
                "shots_target_val": round(shots_target * mins_factor, 2),
                "age_val": float(age),
            }
            records.append(rec)

        df = pd.DataFrame(records)
        df.fillna(0.0, inplace=True)
        self._dataframe = df
        self._is_loaded = True
        return df

    def load_dataset(self, filename: str = "players.csv") -> dict:
        """Load a static player dataset from backend/ml/data/ if present."""
        filepath = os.path.join(self.DATASET_DIR, filename)

        if not os.path.exists(filepath):
            return {
                "status": "no_dataset",
                "message": f"No dataset found at '{filepath}'. Dynamic API data fallback active.",
            }

        try:
            df = pd.read_csv(filepath)
            self._dataframe = df
            self._is_loaded = True
            return {"status": "loaded", "rows": len(df), "columns": list(df.columns)}
        except Exception as e:
            return {"status": "error", "message": f"Failed to load dataset: {str(e)}"}

    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Return the preprocessed DataFrame."""
        return self._dataframe

    @staticmethod
    def _safe_float(val: Any, default: float = 0.0) -> float:
        """Safely parse float values from string or None without throwing exceptions."""
        if val is None or val == "" or val == "Not available" or val == "N/A":
            return default
        try:
            return float(str(val).replace("%", "").strip())
        except (ValueError, TypeError):
            return default


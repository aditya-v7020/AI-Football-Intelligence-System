# ML Module — Dataset-Ready Architecture

This module is prepared for future machine learning integration.

## How to Add a Dataset

1. Place your CSV/JSON dataset file in `backend/ml/data/`
2. Update `preprocessor.py` → `load_dataset()` with the correct file path and column mappings
3. Implement `clean_data()` and `engineer_features()` based on your dataset structure
4. Update `similarity.py` → `find_similar()` with your feature columns
5. Update `recommender.py` → `recommend()` to combine ML results with API data

## Expected Dataset Columns (minimum)

| Column | Description |
|--------|-------------|
| `name` | Player full name |
| `age` | Player age |
| `position` | Playing position |
| `nationality` | Country |
| `team` | Current club |
| `league` | League name |
| `goals` | Total goals |
| `assists` | Total assists |
| `appearances` | Matches played |
| `minutes` | Minutes played |
| `rating` | Overall rating |

Additional columns (shooting, passing, dribbling, defending, etc.) will improve similarity results.

## Architecture

- `preprocessor.py` — Load, clean, and feature-engineer the dataset
- `similarity.py` — Cosine similarity / KNN for finding similar players
- `recommender.py` — Combines ML similarity with API-Football and Tavily data

All classes return meaningful "no dataset available" messages until a real dataset is provided.
No fake data or fake ML results are ever generated.

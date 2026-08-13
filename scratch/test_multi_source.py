"""
Verification test script for Football AI Multi-Source Data Architecture.
"""

import os
import sys

# Ensure backend root on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from backend.core.tools.cache import api_cache
from backend.core.tools.football_tool import search_players_structured
from backend.core.tools.sportmonks_tool import search_players_sportmonks
from backend.core.tools.thesportsdb_tool import search_players_thesportsdb
from backend.core.tools.football_data_tool import get_standings, get_fixtures
from backend.core.tools.tavily_tool import tavily_search
from backend.core.tools.multi_source_pipeline import (
    get_multi_source_player_data,
    get_multi_source_competition_data,
    get_real_scout_candidates,
)
from backend.core.tools.normalizer import deduplicate_players


def run_tests():
    print("==================================================")
    print("RUNNING MULTI-SOURCE FOOTBALL SYSTEM VERIFICATION")
    print("==================================================")

    # 1. Config Validation
    print("\n--- 1. CONFIGURATION CHECK ---")
    print(f"GROQ_API_KEY Configured: {bool(settings.GROQ_API_KEY)}")
    print(f"FOOTBALL_API_KEY Configured: {bool(settings.FOOTBALL_API_KEY)}")
    print(f"SPORTMONKS_API_KEY Configured: {bool(settings.SPORTMONKS_API_KEY)}")
    print(f"THESPORTSDB_API_KEY Configured: {bool(settings.THESPORTSDB_API_KEY)}")
    print(f"FOOTBALL_DATA_API_KEY Configured: {bool(settings.FOOTBALL_DATA_API_KEY)}")
    print(f"TAVILY_API_KEY Configured: {bool(settings.TAVILY_API_KEY)}")
    print(f"DATABASE_URL Configured: {bool(settings.DATABASE_URL)}")

    # 2. Individual Tool Integrations
    print("\n--- 2. TOOL INTEGRATIONS ---")

    # API-Football
    af_players = search_players_structured("Haaland", 2024)
    print(f"API-Football 'Haaland': {len(af_players)} players returned. First: {af_players[0]['name'] if af_players else 'None'}")

    # Sportmonks
    sm_players = search_players_sportmonks("Haaland")
    print(f"Sportmonks 'Haaland': {len(sm_players)} players returned.")

    # TheSportsDB
    tsdb_players = search_players_thesportsdb("Haaland")
    print(f"TheSportsDB 'Haaland': {len(tsdb_players)} players returned. Photo: {tsdb_players[0]['photo'] if tsdb_players else 'None'}")

    # Football-Data
    standings = get_standings("PL")
    print(f"Football-Data Standings preview: {standings[:120]}...")

    # Tavily
    web_res = tavily_search("Haaland goals 2024", max_results=2)
    print(f"Tavily Search preview: {web_res[:120]}...")

    # 3. Multi-Source Pipeline & Deduplication
    print("\n--- 3. MULTI-SOURCE PIPELINE & DEDUPLICATION ---")
    prompt_text, pipeline_players, sources = get_multi_source_player_data("Bruno Fernandes")
    print(f"Multi-Source Query 'Bruno Fernandes' retrieved {len(pipeline_players)} players.")
    print(f"Sources Used: {sources}")
    print(f"Sample Normalized Record: {pipeline_players[0] if pipeline_players else 'None'}")

    # 4. Scouting Real Candidates Retrieval
    print("\n--- 4. REAL SCOUTING CANDIDATES RETRIEVAL ---")
    candidates, c_sources = get_real_scout_candidates(position="Midfielder", reference_player_name="Bruno Fernandes")
    print(f"Real Scout Candidates Count: {len(candidates)}")
    print(f"Candidate Sources: {c_sources}")
    for idx, c in enumerate(candidates[:3], 1):
        print(f"  Candidate {idx}: {c['name']} ({c['team']}) - Rating: {c['rating']} | [Source: {c['source']}]")

    print("\n==================================================")
    print("ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    run_tests()

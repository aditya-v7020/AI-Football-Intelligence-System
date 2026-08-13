import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_API_KEY")

BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_API_KEY")


def search_players(query):
    url = "https://v3.football.api-sports.io/players"

    headers = {
        "x-apisports-key": API_KEY
    }

    params = {
        "search": query,
        "season": 2025
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10
    )

    data = response.json()

    players = []

    if "response" in data:

        for item in data["response"][:5]:

            player = item.get("player", {})
            statistics = item.get("statistics", [])

            name = player.get("name", "Unknown")
            age = player.get("age", "Unknown")
            nationality = player.get("nationality", "Unknown")

            position = "Unknown"
            team = "Unknown"
            league = "Unknown"
            appearances = 0
            goals = 0
            assists = 0

            if statistics:
                stats = statistics[0]

                position = stats.get(
                    "games", {}
                ).get("position", "Unknown")

                appearances = stats.get(
                    "games", {}
                ).get("appearences", 0)

                team = stats.get(
                    "team", {}
                ).get("name", "Unknown")

                league = stats.get(
                    "league", {}
                ).get("name", "Unknown")

                goals = stats.get(
                    "goals", {}
                ).get("total", 0)

                assists = stats.get(
                    "goals", {}
                ).get("assists", 0)

            players.append(
                f"""
Player: {name}
Age: {age}
Nationality: {nationality}
Team: {team}
League: {league}
Position: {position}
Appearances: {appearances}
Goals: {goals}
Assists: {assists}
"""
            )

    return "\n".join(players)
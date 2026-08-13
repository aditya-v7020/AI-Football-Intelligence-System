import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)


def tavily_search(query):
    try:
        response = tavily_client.search(
            query=query,
            search_depth="basic",
            max_results=5
        )

        results = []

        for item in response.get("results", []):
            title = item.get("title", "Unknown")
            content = item.get("content", "No information available")
            url = item.get("url", "")

            results.append(
                f"""
Title: {title}
Information: {content}
Source: {url}
"""
            )

        if not results:
            return "No web search results found."

        return "\n".join(results)

    except Exception as e:
        return f"Tavily search error: {str(e)}"
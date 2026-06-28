import os

from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def get_client():

    if not TAVILY_API_KEY:
        return None

    try:
        from tavily import TavilyClient

        return TavilyClient(api_key=TAVILY_API_KEY)

    except ImportError:
        return None


def tavily_search(
    query: str,
    max_results: int = 5,
) -> str:
    """
    Perform Tavily web search.
    """

    client = get_client()

    if client is None:
        return (
            "Tavily search unavailable. "
            "Check API key or package installation."
        )

    try:

        response = client.search(
            query=query,
            max_results=max_results,
        )

    except Exception as e:
        return f"Tavily search failed: {e}"

    results = response.get("results", [])

    if not results:
        return "No search results found."

    output = []

    for index, item in enumerate(results, start=1):

        title = item.get("title", "Untitled")

        url = item.get("url", "")

        snippet = item.get("content", "").strip()

        if len(snippet) > 300:
            snippet = snippet[:300].rsplit(" ", 1)[0] + "..."

        output.append(
            f"""{index}. {title}

URL:
{url}

Summary:
{snippet}
"""
        )

    return "\n\n".join(output)
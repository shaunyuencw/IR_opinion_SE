import os
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

# Retrieve the SerpApi key from environment variables
SERPAPI_KEY = os.environ.get("SERPER_DEV")
SERPAPI_BASE_URL = "https://serpapi.com/search?engine=google_news"

class SearchQuery(BaseModel):
    query: str

def get_news_params(query, country_code=None, sort_by=None):
    """
    Constructs the parameters for the news search query.
    :param query: The search query.
    :param country_code: Two-letter country code for localization, optional.
    :param sort_by: Sort method ('0' for Relevance, '1' for Date), optional.
    """
    params = {
        "engine": "google_news",
        "q": query,
        "api_key": SERPAPI_KEY
    }
    if country_code:
        params["gl"] = country_code
    if sort_by in ['0', '1']:
        params["so"] = sort_by
    return params

async def fetch_news(query: str, country_code: str = None, sort_by: str = None):
    params = get_news_params(query, country_code, sort_by)
    async with httpx.AsyncClient() as client:
        response = await client.get(SERPAPI_BASE_URL, params=params)
        response.raise_for_status()  # Will raise exception for 4XX/5XX responses
        return response.json()


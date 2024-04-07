from fastapi import FastAPI, HTTPException
from models.Ticker import *
from models.LLM import *
from models.News import *
import httpx

app = FastAPI()
url = "https://google.serper.dev/news"

# Asynchronous endpoint to fetch ticker data
@app.get("/info/{ticker}", response_model=TickerInfo)
async def get_ticker_info(ticker: str):
    ticker_data = Ticker(ticker=ticker)
    
    # Fetch news for the ticker
    try:
        news_results = await fetch_news(ticker)  # You might want to customize the query
        ticker_data.news = news_results["news_results"] # Assuming Ticker class can store the news or modify as needed
    except httpx.HTTPStatusError as e:
        print(f"Failed to fetch news for {ticker}: {e.response.text}")
        ticker_data.news = "News fetch failed"
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        ticker_data.news = "News fetch failed"

    # Return the combined ticker and news information
    return TickerInfo(
        name=ticker_data.name,
        news=ticker_data.news,
        info=ticker_data.info
    )


# Modify the function to accept a POST request and use the NewsArticle model
@app.post("/summarize")
async def summarize_news(article: NewsArticle):
    palm_interface = PalmInterface()
    summary = palm_interface.summarize(article.news)
    
    print(summary)
    return summary


@app.get("/search-news")
async def search_news(query: str, country_code: str = None, sort_by: str = None):
    """
    Fetch news based on a search query using SerpApi.
    """
    news_results = await fetch_news(query, country_code, sort_by)
    return news_results
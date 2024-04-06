import yfinance as yf
from pydantic import BaseModel


# Define a class to fetch ticker data
class Ticker:
    def __init__(self, ticker):
        self.ticker = ticker
        self.socket = yf.Ticker(self.ticker)
        self.name = (self.socket.info.get("longName", "N/A"),)
        self.news = self.socket.news if self.socket.news is not None else []
        self.info = {
            "sector": self.socket.info.get("sector", "N/A"),
            "summary": self.socket.info.get("longBusinessSummary", "N/A"),
            "country": self.socket.info.get("country", "N/A"),
            "website": self.socket.info.get("website", "N/A"),
            "employees": self.socket.info.get("fullTimeEmployees", "N/A"),
        }


# Define a Pydantic model for your API response
class TickerInfo(BaseModel):
    name: tuple
    news: list
    info: dict

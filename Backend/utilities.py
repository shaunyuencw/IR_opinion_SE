import yfinance as yf
from pydantic import BaseModel


# Define a class to fetch ticker data
class Ticker:
    def __init__(self, ticker):
        self.ticker = ticker
        self.socket = yf.Ticker(self.ticker)
        self.name = self.socket.info['longName'],
        self.news = self.socket.news
        self.info = {
            "sector": self.socket.info["sector"],
            "summary": self.socket.info["longBusinessSummary"],
            "country": self.socket.info["country"],
            "website": self.socket.info["website"],
            "employees": self.socket.info["fullTimeEmployees"]
        }

# Define a Pydantic model for your API response
class TickerInfo(BaseModel):
    name: tuple
    news: list
    info: dict

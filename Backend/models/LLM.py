import google.generativeai as palm
import os
import json
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

palm.configure(api_key=os.environ["PALM2_API_TOKEN"])

class NewsArticle(BaseModel):
    news: str

class PalmInterface:
    def prompt(self, query):
        try:
            payload = self.build_input(query)
            defaults = {"model": "models/text-bison-001"}

            response = palm.generate_text(**defaults, prompt=payload)

            # json_response = response.get("candidates",None).get("output",None)
            json_response = json.loads(response.result)
            # print(json_response)
            return json_response
        except Exception as e:
            print(e)
            return None

    def summarize(self, full_news):
        template = f"Given a news article, your task is to provide a concise, coherent summary that captures the main points and details critical to understanding the article's content and context. \
        The summary should be accurate and maintain the integrity of the original article, ensuring that key facts, figures, and names are preserved. \
        Additionally, you are to analyze the overall sentiment of the article—whether it's positive, negative, or neutral—and provide a sentiment score. \
        The sentiment score should range from -1 (highly negative) to 1 (highly positive), with 0 representing a neutral sentiment. \
        \n\nYour output should be structured in JSON format, containing two key-value pairs: 'summarize_news' for the article summary and 'sentiment_analysis_score' for the sentiment score. \
        Ensure the summary is succinct and does not exceed the length of the original text. \
        \n\nPlease proceed with analyzing the news article provided and return the requested information in the specified format. \n\n{full_news}"

        try:
            defaults = {"model": "models/text-bison-001"}
            response = palm.generate_text(**defaults, prompt=template)
            return response.result
        except Exception as e:
            print(e)
            return None

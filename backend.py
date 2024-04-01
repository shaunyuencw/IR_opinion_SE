from fastapi import FastAPI, Form
from pydantic import BaseModel

import helpers
import random

import torch
from langchain_community.llms import Ollama

# Packages
# fastapi, pydantic, torch, langchain_community, pandas, pyyaml, bs4

# Backend Params
MAX_ARTICLES = 20

app = FastAPI()
url = "https://google.serper.dev/news"

system_instruct = """
The user will provide an input topic and a raw news article. The system will clean the raw news article text for sentiment analysis focused on the given topic. Do this by following these rules strictly:

**Rule 1: Remove Non-Article Elements**
*  Delete advertisements, error messages, disclaimers, links, author information, post-article recommendations, embedded social media widgets, subscription prompts, and any other items that are not sentences from the main article body.
* **Focus on Format:** Identify these elements based primarily on their structure and common patterns  (e.g., email signatures, "Read More" links, disclaimers in smaller fonts, sections clearly separated by visual dividers).

**Rule 2: Isolate Relevant Content**
* **Direct Keyword Match:** Keep sentences containing ANY of the provided keywords.
* **Context Preservation:**  If a sentence doesn't contain a keyword but is ESSENTIAL to understanding the flow and meaning of subsequent keyword-containing sentences, keep it. 
* **No Rephrasing:** Maintain the article's original structure and wording as precisely as possible. Do not attempt ANY rephrasing or simplification.
 
The system will output the cleaned article text for sentiment analysis.
Cleaned Article: <Article>
"""

# Load configuration
config = helpers.load_config('config.yaml')
device = "mps" if torch.backends.mps.is_available() else "cpu" # If using Apple Silicon
llm = Ollama(model="gemma", system=system_instruct, num_ctx=8192, num_predict=1024, temperature=0, top_k=0, top_p=0)

def get_sentiment(article):
    # TODO - Add in model for sentiment analysis here
    return random.uniform(-1, 1)

class SentimentRequestForm(BaseModel):
    query_topic: str
    num_articles: int
    llm_clean: bool = False

@app.post("/get_sentiments/")
async def get_sentiments(query_topic: str = Form(...), num_articles: int = Form(...), llm_clean: bool = Form(False)):
    if num_articles > MAX_ARTICLES:
        return {
            "error": "The number of articles must be less than or equal to 20."
        }

    payload = {
        "query": query_topic,
        "num_articles": num_articles
    }

    headers = {
        'X-API-Key': config['api_key'],
        'Content-Type': 'application/json'
    }

    data = helpers.fetch_data(url, payload, headers, query_topic) # Grabs recent articles from the API
    article_sources = data['news']

    article_list = []
    sentiment_scores = []

    for i, article in enumerate(article_sources):
        article_url = article['link']
        article_body = helpers.fetch_article_body(article_url)

        if llm_clean: # * This is time intensive, so only do it if the user specifies
            prompt = f"""
Input Topic: {query_topic} \n
Raw Article: {article_body}
"""
            article_body = helpers.extract_plain_text(llm.invoke(prompt))
            if helpers.check_invalid(article_body):
                continue

        sentiment = get_sentiment(article_body)

        sentiment_scores.append(sentiment)
        article_list.append({
            "title": article['title'],
            "source": article['source'],
            "url": article_url,
            "article_body": article_body,
            "sentiment": sentiment
        })
        print(f"Processed article {i + 1}/{num_articles}")

        if len(article_list) >= num_articles:
            break
       
    overall_sentiment =  sum(sentiment_scores) / len(sentiment_scores) # TODO - Implement a better way to calculate overall sentiment

    return {
        "query_topic": query_topic,
        "overall_sentiment": overall_sentiment, 
        "articles": article_list 
    }



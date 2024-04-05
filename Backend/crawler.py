import requests
import json
import os
import yaml
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys
import re

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import time

from langchain_community.llms import Ollama
import csv
import json
from typing import Tuple, List

def load_config(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def save_results(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def load_results(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def fetch_data(url, payload, headers, search_term):
    # Ensure the cache directory exists
    cache_dir = 'cache'
    os.makedirs(cache_dir, exist_ok=True)
    
    # Generate the file path based on the search term
    file_name = f"{search_term.lower()}.json"
    file_path = os.path.join(cache_dir, file_name)
    
    if os.path.exists(file_path):
        print(f"Found cached data for {search_term}...")
        data = load_results(file_path)
    else:
        print("Fetching data from the API...")
        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        save_results(file_path, data)
        print(f"Data saved to {file_path}")
    return data

def fetch_article_body(url):
    """
    Fetches the body of a news article given its URL, focusing on extracting and cleaning the main content.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Check for HTTP request errors
        soup = BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        # print(f"Error fetching the article: {e}, skipping...")
        return "No content"

    # Define a list of selectors that likely contain the main article content.
    content_selectors = [
        'article', 
        'div.article-content',  # Add or modify selectors based on common patterns across websites.
        'main',
        'div#main-content'
    ]

    article = None
    # Iterate over selectors to find the main content container.
    for selector in content_selectors:
        article = soup.select_one(selector)
        if article:
            break

    if not article:
        article = soup  # Fallback to using the entire soup if no specific container is found.

    # Remove non-article elements specified by tag or class.
    for tag in ['script', 'style', 'footer', 'nav', 'header']:
        for element in article.find_all(tag):
            element.decompose()

    # For classes that are more specific and don't correspond to a whole tag, you can add them here.
    non_article_classes = ['nav-menu-mainLinks', 'account-menu-accountMenu', 'CNBCFooter-wrapper', 'footer-class']
    for non_article_class in non_article_classes:
        for element in article.find_all(class_=non_article_class):
            element.decompose()

    # Clean and return the text.
    text = ' '.join(article.stripped_strings)
    return text

# Function to read existing data and return a set of tuples (topic, article_link)
def read_existing_data(filepath):
    existing_data = set()
    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_data.add((row['topic'], row['article_link']))
    except FileNotFoundError:
        # If the file does not exist, return an empty set
        pass
    return existing_data

def clean_article_text(text):
    # Remove leading/trailing whitespace
    text = text.replace('Cleaned Article Text', '')
    text = text.replace('Cleaned Article', '')
    text = text.replace('‚Äô', '\'')
    text = text.replace('‚Äì', '-')

    # Remove all newline characters
    text = re.sub(r'\\n|\*|^##\s*', ' ', text)

    # Remove asterisks and other special characters
    text = re.sub(r'[*]+', '', text)

    # Remove extra whitespace between words
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def extract_plain_text(article):
    parts = article.split("Cleaned Article:")
    if len(parts) >= 2:
        return parts[1]
    else:
        return article
    
def estimate_sentiment(news_item: str, allow_neutral: bool = True) -> Tuple[str, float]:
    """
    Estimates sentiment for an individual news item, returning the sentiment label and its confidence score.
    If 'allow_neutral' is False and the top sentiment is 'neutral', it returns the second-highest sentiment and its confidence.
    """
    tokens = tokenizer(news_item, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
    with torch.no_grad():  # Inference mode
        result = model(tokens["input_ids"], attention_mask=tokens["attention_mask"])["logits"]
    softmax_results = torch.nn.functional.softmax(result, dim=-1)[0]  # Take first item's results

    if not allow_neutral:
        # Sort the results to get the indices of the sentiments in descending order of confidence
        sorted_indices = torch.argsort(softmax_results, descending=True)
        if labels[sorted_indices[0]] == "neutral":
            # If the top sentiment is neutral, use the second-highest confidence sentiment
            max_index = sorted_indices[1]
        else:
            max_index = sorted_indices[0]
    else:
        max_index = torch.argmax(softmax_results)

    sentiment = labels[max_index]
    confidence = softmax_results[max_index].item()  # Convert to Python float

    return sentiment, confidence

# Topics of interest
with open("data/topics.txt", "r") as file:
    financial_topics = [line.strip() for line in file][7:] # TOPICS

# Load configuration
config = load_config('config.yaml')
device = "mps" if torch.backends.mps.is_available() else "cpu" # If using Apple Silicon

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(device)
labels = ["positive", "negative", "neutral"]

news = []
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

llm = Ollama(model="gemma", system=system_instruct, num_ctx=8192, num_predict=1024, temperature=0, top_k=0, top_p=0)

csv_file_path = 'data/crawled_data.csv'

existing_data = read_existing_data(csv_file_path)

file_exists = os.path.isfile(csv_file_path)

with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['topic', 'title', 'source', 'article_link', 'article', 'sentiments'])
    # Write the header only if the file did not exist prior to opening it
    if not file_exists:
        writer.writeheader()

for search_query in financial_topics:
    num_articles = 100
    payload = json.dumps({
        "q": search_query,
        "num": num_articles,    
    })
    headers = {
        'X-API-KEY': config['api_key'],
        'Content-Type': 'application/json'
    }

    print(f"Processing {search_query}...")
   
    data = fetch_data(url, payload, headers, search_query)
    
    if data and "news" in data and len(data["news"]) > 0:
        topic = search_query.split(' (')[0]
        # Initialize tqdm with the total count to enable manual control
        pbar = tqdm(total=len(data["news"][:num_articles]), desc="Fetching Articles", miniters=0.05)

        for article in data["news"][:num_articles]:
            sys.stdout.flush()  
            title = article.get('title', 'No title')
            source = article.get('source', 'No source')
            article_link = article.get('link', '')

            # Check if this topic and link combination already exists
            if (topic, article_link) in existing_data:
                pbar.update(1)
                time.sleep(0.1)
                continue
            
            # print("Fetching article body...", article_link)
            article_body = fetch_article_body(article_link) if article_link else 'No content'
            # print("Fetched article body...")

            if article_body == 'No content':
                pbar.update(1)
                time.sleep(0.1)
                continue

            article_body = article_body.replace('\n', 'nl')
            
            prompt = f"""
Input Topic: {topic} \n
Raw Article: {article_body}
"""
            # Here you would clean the article_body as before
            cleaned_article = extract_plain_text(llm.invoke(prompt))
            cleaned_article = cleaned_article.replace('\n', '\\n')

            cleaned_article = clean_article_text(cleaned_article)

            # Estimate the sentiment of the cleaned article
            sentiments, _ = estimate_sentiment(cleaned_article, allow_neutral=True)

            title = title.replace('\n', ' ').replace('\r', ' ')

            with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['topic', 'title', 'source', 'article_link', 'article', 'sentiments'])
                writer.writerow({
                    'topic' : topic,
                    'title': title,
                    'source': source,
                    'article_link': article_link,
                    'article': cleaned_article,
                    'sentiments': sentiments
                })
            pbar.update(1)  # Manually increment the progress bar
        pbar.close()

# TODO CLEAN ROWS up to 2056
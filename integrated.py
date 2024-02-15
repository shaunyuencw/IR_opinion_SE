import requests
import json
import os
import yaml
import re
from bs4 import BeautifulSoup
from collections import Counter
from tqdm import tqdm

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
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
        print(f"Loading data from {file_path}...")
        data = load_results(file_path)
    else:
        print("Fetching data from the API...")
        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        save_results(file_path, data)
        print(f"Data saved to {file_path}")
    return data

def get_main_content(soup):
    """
    Attempts to find and return the main content of the article.
    This function tries to identify the container most likely to hold the main text based on common class names and tags.
    """
    # Common selectors for the main content of an article. Adjust based on common patterns.
    selectors = [
        'article',  # <article> tags
        'div.article-content',  # divs with a class of 'article-content'
        'main',  # <main> tags, often used to wrap the primary content
        'div#main-content',  # div with an ID of 'main-content'
        # Add or modify selectors based on the sites you're targeting
    ]
    
    for selector in selectors:
        content = soup.select_one(selector)
        if content:
            return content
    
    # Fallback to the entire body if specific content wasn't found
    return soup.body

def clean_and_extract_text(content):
    """
    Cleans the extracted HTML content and returns clean text.
    """
    # Remove script and style elements
    for script_or_style in content(['script', 'style']):
        script_or_style.decompose()

    # Get text from the HTML
    text = content.get_text(separator=' ', strip=True)

    # Post-processing to remove any extra spaces and newlines
    text = re.sub(r'\s+', ' ', text)
    
    return text

def cut_off_extra_content(text):
    """
    Cuts off the text at the first occurrence of phrases indicating the end of the main content.

    :param text: The text to be processed.
    :return: The text cut off at the point where extra content (like "Related Posts") starts.
    """
    # Compile a regular expression pattern to match phrases that typically indicate the end of main content
    pattern = re.compile(r'(Related Posts|Most Read|Recent News|See Full Event Calendar)', re.IGNORECASE)

    # Search for the pattern in the text
    match = pattern.search(text)
    if match:
        # If a match is found, cut the text up to the start of the matched phrase
        return text[:match.start()].strip()
    else:
        # If no such phrases are found, return the original text
        return text

def fetch_article_body(url):
    """
    Fetches the body of a news article given its URL, focusing on extracting and cleaning the main content.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Attempt to directly find the main content container. Adjust based on the site's structure.
    article = soup.find('article')
    if not article:
        article = soup.find('div', attrs={'class': 'article-content'})  # Example class, adjust accordingly.

    # If specific content containers are not found, fall back to broader content and manual exclusions.
    if not article:
        article = soup

    # Exclude known non-article elements such as footers, headers, and nav bars.
    # This requires knowing class names or IDs specific to these elements.
    for non_article_section in article.find_all(['footer', 'nav', 'header', 'div'], 
                                                 attrs={'class': ['nav-menu-mainLinks','account-menu-accountMenu', 'CNBCFooter-wrapper', 'footer-class', 'nav-class', 'header-class', 'non-article-div-class']}):  # Example classes/IDs
        non_article_section.decompose()

    # Clean and return the text.
    text = ' '.join(article.stripped_strings)
    return text

def save_news_to_file(news_text, file_path):
    """
    Saves cleaned news text to a specified text file.

    :param news_text: The cleaned news text to save.
    :param file_path: The path (including file name) where to save the text.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(news_text)
    print(f"News text saved to {file_path}")

def load_news_from_file(file_path):
    """
    Loads news text from a specified text file.

    :param file_path: The path (including file name) of the text file to load.
    :return: The content of the news text file as a string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"No file found at {file_path}")
        return None

def estimate_individual_sentiment(news_item: str, allow_neutral: bool = True) -> Tuple[str, float]:
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


def estimate_and_aggregate_sentiments(news_items: List[str]) -> List[Tuple[str, float]]:
    """
    Estimates sentiments for multiple news items and returns a list of tuples with sentiment labels and confidence scores.
    """
    detailed_sentiments = [estimate_individual_sentiment(news_item, False) for news_item in news_items]
    return detailed_sentiments

def aggregate_sentiments(detailed_sentiments, normalize: bool = True) -> float:
    """
    Aggregates sentiments from multiple news items and calculates a score,
    giving less weight to neutral sentiments in the normalization step.
    """
    score = 0
    total_confidence = 0  # Sum of confidence for non-neutral sentiments

    for sentiment, confidence in detailed_sentiments:
        if sentiment == "positive":
            score += confidence  # Positive contributes to the score
            total_confidence += confidence
        elif sentiment == "negative":
            score -= confidence  # Negative detracts from the score
            total_confidence += confidence
        # Neutral sentiments do not contribute to score or total confidence

    if normalize:
        # Normalize the score by total confidence of non-neutral sentiments
        normalized_score = score / total_confidence if total_confidence > 0 else 0

        return normalized_score
    else:
        return score



# Load configuration
config = load_config('config.yaml')

url = "https://google.serper.dev/news"
search_query = input("What do you want to search for? ")

payload = json.dumps({
  "q": search_query,
})
headers = {
  'X-API-KEY': config['api_key'],
  'Content-Type': 'application/json'
}

news = []
num_articles = 10
data = fetch_data(url, payload, headers, search_query)

# Assuming 'data' is the fetched or loaded data from the 'fetch_data' function
print(f"Fetching articles...")
if data and "news" in data and len(data["news"]) > 0:
    print(f"Found {len(data['news'])} articles.")
    for article in tqdm(data["news"][:num_articles], desc="Fetching Articles"):
        # news.append(article["title"]) #! Not very accurate lol
                    
        article_body = fetch_article_body(article["link"])
        news.append(article_body)

device = "mps" if torch.backends.mps.is_available() else "cpu" # If using Apple Silicon

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(device)
labels = ["positive", "negative", "neutral"]

print(f"Processing and estimating sentiments...")
detailed_sentiments = estimate_and_aggregate_sentiments(news)

for i, article in enumerate(data["news"][:num_articles]):
    print(f"Title: {article.get('title', 'No title')}")
    # print(f"Link: {article.get('link', 'No link')}")

    sentiment, confidence = detailed_sentiments[i]
    print(f"Sentiment: {sentiment} (Confidence: {confidence:.2f})")
    print()

overall_sentiment = aggregate_sentiments(detailed_sentiments, True)
if overall_sentiment > 0.1:
    print(f"The overall sentiment is positive with a score of {overall_sentiment * 100:.2f}")
elif overall_sentiment < -0.1:
    print(f"The overall sentiment is negative with a score of {overall_sentiment * 100:.2f}")
else:
    print(f"The overall sentiment is neutral with a score of {overall_sentiment * 100:.2f}")




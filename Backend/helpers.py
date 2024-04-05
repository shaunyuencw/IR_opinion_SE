import pandas as pd
import re
import yaml
import requests
import os
import json
from bs4 import BeautifulSoup

def clean_article_text(text):
    if pd.isna(text):
        return ''

    # Convert to string to ensure compatibility with replace and regex operations
    text = str(text)

    # Consolidate replacements for efficiency and readability
    replacements = {
        'Cleaned Article Text': '',
        'Cleaned Article': '',
        '‚Äô': '\'',
        '‚Äì': '-',
        '\u2019': '\'',
        '\u2018': '\'',
        '\u2013': '-',
        '\u201C': '"',
        '\u201D': '"'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Compile regular expressions for performance if called frequently
    newline_re = re.compile(r'\\n|\*|^##\s*')
    asterisk_re = re.compile(r'[*]+')
    whitespace_re = re.compile(r'\s+')

    # Apply compiled regex
    text = newline_re.sub(' ', text)
    text = asterisk_re.sub('', text)
    text = whitespace_re.sub(' ', text)

    return text.strip()

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

def extract_plain_text(article):
    parts = article.split("Cleaned Article:")
    if len(parts) >= 2:
        return parts[1]
    else:
        return article
    
def check_invalid(article):
    invalid_phrases = ['cannot complete the task', 'does not contain']

    for phrase in invalid_phrases:
        if phrase in article:
            return True

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
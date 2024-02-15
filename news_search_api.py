import requests
import json
import os
import yaml
import re
from bs4 import BeautifulSoup

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

data = fetch_data(url, payload, headers, search_query)
# Assuming 'data' is the fetched or loaded data from the 'fetch_data' function
if data and "news" in data and len(data["news"]) > 0:
    first_news_item = data["news"][0]  # Access the first news item
    print("First News Item:")
    print(f"Title: {first_news_item.get('title', 'No title')}")
    print(f"Link: {first_news_item.get('link', 'No link')}")

    print("\nFetching article body...")
    article_body = fetch_article_body(first_news_item["link"])
    print(article_body)
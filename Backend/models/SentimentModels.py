from bs4 import BeautifulSoup
import requests
from pydantic import BaseModel

class Link(BaseModel):
    url: str

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
    # #remove space
    text = ' '.join(article.stripped_strings)
    # no_space_text = text.replace(" ", "")

    # #remove ,.
    # punctuation = string.punctuation
    # translator = str.maketrans('', '', punctuation)
    # clean_text = no_space_text.translate(translator)

    return text
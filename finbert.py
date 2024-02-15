from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Tuple, List
device = "mps" if torch.backends.mps.is_available() else "cpu" # If using Apple Silicon

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(device)
labels = ["positive", "negative", "neutral"]

def estimate_individual_sentiment(news_item: str) -> Tuple[torch.Tensor, str]:
    """
    Estimates sentiment for an individual news item.
    """
    tokens = tokenizer(news_item, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
    with torch.no_grad():  # Inference mode
        result = model(tokens["input_ids"], attention_mask=tokens["attention_mask"])["logits"]
    result = torch.nn.functional.softmax(result, dim=-1)[0]  # Take first item's results
    return result, labels[torch.argmax(result)]

def aggregate_sentiments(sentiments: List[torch.Tensor]) -> str:
    """
    Aggregates sentiments from multiple news items and returns the dominant sentiment.
    """
    # Sum sentiment scores and find dominant sentiment
    total_sentiment = torch.sum(torch.stack(sentiments), dim=0)
    dominant_sentiment = labels[torch.argmax(total_sentiment)]
    return dominant_sentiment

def estimate_sentiment(news_items: List[str]) -> str:
    """
    Estimates and aggregates sentiment from multiple news items.
    """
    sentiments = []
    for news_item in news_items:
        result, _ = estimate_individual_sentiment(news_item)
        sentiments.append(result)
    overall_sentiment = aggregate_sentiments(sentiments)
    return overall_sentiment

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


if __name__ == "__main__":
    news = []
    news.append(load_news_from_file("cache/news.txt"))
    sentiment = estimate_sentiment(news)

    # sentiment = estimate_sentiment(['Tesla fucked up everything!','traders revolt!'])
    print(sentiment)
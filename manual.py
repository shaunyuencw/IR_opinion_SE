import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Tuple, List
from langchain_community.llms import Ollama
import re

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
    
def load_dataset(csv_file_path):
    return pd.read_csv(csv_file_path, encoding='utf-8')

def get_dataset_column(dataset, column):
    return dataset[column].unique()

def filter_dataset(dataset, column, value):
    return dataset[dataset[column] == value]

def get_random_row(dataset):
    return dataset.sample(1)


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

# Load model
device = "mps" if torch.backends.mps.is_available() else "cpu" # If using Apple Silicon

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(device)
labels = ["positive", "negative", "neutral"]

# Load data/temp.txt
with open("data/temp.txt") as f:
    article = f.read()

topic = "Berkshire Hathaway"

prompt = f"""
Input Topic: {topic} \n
Raw Article: {article}
"""

# Summarize the article
article = llm.invoke(prompt)
article = clean_article_text(article)

# Write back to data/temp.txt
with open("data/out.txt", "w") as f:
    f.write(article)

# Estimate sentiment
sentiment, confidence = estimate_individual_sentiment(article, True)
print(f"Sentiment: {sentiment}, Confidence: {confidence}")


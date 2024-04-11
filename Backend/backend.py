from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from models.Ticker import *
from models.LLM import *
from models.News import *
from models.ElasticSearch import *
from models.SentimentModels import *
from typing import List, Optional
import httpx
import response_info_tsla
import response_search_news
from pprint import pprint

# Sentiment Analysis imports
import pickle
import torch
import numpy as np
from torch.nn.functional import softmax
from transformers import BertTokenizer, RobertaTokenizer
from collections import Counter

app = FastAPI()

# Add a middleware to allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],  # Adjust the allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Or specify the allowed methods
    allow_headers=["*"],  # Or specify the allowed headers
)

# Initialize models and tokenizers to None
bert_model, tokenizer, roberta_model, tokenizer_r, svm_neutral_model, svm_opinion_model = (None, None, None, None, None, None)

def load_models():
    global bert_model, tokenizer, roberta_model, tokenizer_r, svm_neutral_model, svm_opinion_model

    # Load BERT model and tokenizer
    bert_model_path = "models/BERT/model_full.pth"
    bert_model = torch.load(bert_model_path, map_location='cpu')
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    # Load RoBERTa model and tokenizer
    roberta_model_path = "models/roBERTa/model_full.pth"
    roberta_model = torch.load(roberta_model_path, map_location='cpu')
    tokenizer_r = RobertaTokenizer.from_pretrained('roberta-base')

    # # Load SVM models
    # with open('models/SVMs/neutral_model.sav', 'rb') as f:
    #     svm_neutral_model = pickle.load(f)
    # with open('models/SVMs/pos_neg_model.sav', 'rb') as f:
    #     svm_opinion_model = pickle.load(f)

# Load models at the start
load_models()

#Sentiment Classification and Confidence Score Function
def sentiment_output(input_text):
    #BERT PREDICTION
    bert_input = tokenizer(input_text, padding=True, truncation=True, max_length=512, return_tensors="pt")

    if torch.cuda.is_available():
        bert_input = {k: v.to("cuda") for k, v in bert_input.items()}
        bert_model.to("cuda")

    # Get predictions
    with torch.no_grad():
        outputs = bert_model(**bert_input)
    probs = softmax(outputs.logits, dim=-1)
    
    predicted_class = torch.argmax(probs, dim=-1).item()

    #Get BERT sentiment and confidence
    bert_sentiment = predicted_class
    bert_confidence = probs[0, predicted_class].item()

    #roBERTa PREDICTION

    roberta_input = tokenizer_r(input_text, padding=True, truncation=True, max_length=512, return_tensors="pt")

    if torch.cuda.is_available():
        roberta_input = {k: v.to("cuda") for k, v in roberta_input.items()}
        roberta_model.to("cuda")

    # Get predictions
    with torch.no_grad():
        roberta_outputs = roberta_model(**roberta_input)
    roberta_probs = softmax(roberta_outputs.logits, dim=-1)
    
    roberta_predicted_class = torch.argmax(roberta_probs, dim=-1).item()

    #Get BERT sentiment and confidence
    roberta_sentiment = roberta_predicted_class
    roberta_confidence = roberta_probs[0, roberta_predicted_class].item()

    #SVM PREDICTION
    # check_neutrality = svm_neutral_model.predict_proba([input_text])[0]
    
    # best_confidence = max(check_neutrality)
    # svm_sentiment = np.argmax(check_neutrality)
    
    # check_polarity = svm_opinion_model.predict_proba([input_text])[0]
    # polarity_confidence = max(check_polarity)
    
    # if svm_sentiment == 0:
    #     svm_sentiment = 1
    #     svm_confidence = best_confidence
    
    # else:
    #     if np.argmax(check_polarity) == 0:
    #         svm_sentiment = 0
    #     else:
    #         svm_sentiment = 2
    #     svm_confidence = polarity_confidence
    # svm_con_arr = [check_polarity[0],check_neutrality[0],check_polarity[1]]

    #Final sentiment and Final Confidence
    predictions = [bert_sentiment, roberta_sentiment]
    count = Counter(predictions)
    final_sentiment, num_occurrences = count.most_common(1)[0]

    # Check if there is a majority
    if num_occurrences == 1:
        #print("FLAG 1")
        #SVM is used as tiebreaker
        # if svm_sentiment in predictions:
        #     final_sentiment = svm_sentiment
        #     final_confidence = (probs[0, final_sentiment].item() + roberta_probs[0, final_sentiment].item() + svm_con_arr[final_sentiment]) /3
        #If still tie, roBERTa is used as the final sentiment
        # else:
        final_sentiment = roberta_sentiment
        final_confidence = (probs[0, final_sentiment].item() + roberta_probs[0, final_sentiment].item()) /2
    else:
        #print("FLAG 2")
        final_sentiment = final_sentiment
        final_confidence = (probs[0, final_sentiment].item() + roberta_probs[0, final_sentiment].item()) /2

    labels = ['Negative', 'Neutral', 'Positive']  # Decode the predicted class index back to the label

    return [labels[final_sentiment], final_confidence]

# Query Index with Elastic search
@app.get("/query/", response_model=List[dict])
async def search(search_term: str, exact_phrase: Optional[str] = None, 
                 include_words: Optional[List[str]] = Query(None), exclude_words: Optional[List[str]] = Query(None), 
                 exchange_type: Optional[str] = None):
    elastic = Elastic()
    results = elastic.perform_search(search_term, exact_phrase, include_words, exclude_words, exchange_type)
    return results


# Asynchronous endpoint to fetch ticker data
@app.get("/info/", response_model=TickerInfo)
async def get_ticker_info(ticker: str):
    print("Fetching ticker information...")
    ticker_data = Ticker(ticker=ticker)
    
    # Fetch news for the ticker
    try:
        # news_results = await fetch_news(ticker)
        news_results = response_search_news.data
        flattened_news = flatten_news(news_results)
        print("\tTotal Articles: ", len(flattened_news))
        
        # Get sentiment for each news article
        numerator, denominator = 0, 0
        for news_item in flattened_news:
            # Add the prediction to the each flattened_news
            prediction = predict_sentiment(Link(url=news_item["link"]))
            news_item["sentiment"] = prediction
            # Aggregate the sentiment predictions
            if prediction["sentiment"] == "Positive":
                numerator += (1 * prediction["confidence"])
            else:
                numerator += (-1 * prediction["confidence"])
            denominator += prediction["confidence"]
        
        # Calculate the overall sentiment for the ticker
        sentiment_score = numerator / denominator
        normalized_score = (sentiment_score + 1) / 2
        print("\tNormalized Sentimental Score: ", normalized_score)
    except httpx.HTTPStatusError as e:
        print(f"Failed to fetch news for {ticker}: {e.response.text}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    # Return the combined ticker and news information
    return TickerInfo(
        name=ticker_data.name,
        news=flattened_news,
        info=ticker_data.info,
        sentimental_score=normalized_score
    )


# Modify the function to accept a POST request and use the NewsArticle model
@app.post("/summarize")
async def summarize_news(article: NewsArticle):
    palm_interface = PalmInterface()
    summary = palm_interface.summarize(article.news)
    
    print(summary)
    return summary


@app.get("/search-news")
async def search_news(query: str, country_code: str = None, sort_by: str = None):
    """
    Fetch news based on a search query using SerpApi.
    """
    news_results = await fetch_news(query, country_code, sort_by)
    return news_results


@app.post("/predict")
def predict_sentiment(link: Link):
    input_text = fetch_article_body(link.url)
    sentiment, confidence = sentiment_output(input_text)
    return {"sentiment": sentiment, "confidence": confidence}
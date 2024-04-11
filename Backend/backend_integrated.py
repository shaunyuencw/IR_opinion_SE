from flask import Flask, request, jsonify
import pickle
import torch
import numpy as np
from torch.nn.functional import softmax
from transformers import BertTokenizer, RobertaTokenizer
from collections import Counter
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

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

@app.route('/predict', methods=['POST'])
def predict_sentiment():
    data = request.json
    link = data.get("input_text", "")
    input_text = fetch_article_body(link)
    sentiment, confidence = sentiment_output(input_text)
    return jsonify({"sentiment": sentiment, "confidence": confidence})

if __name__ == '__main__':
    app.run(debug=True)
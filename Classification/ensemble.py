import torch
import pickle
import numpy as np
from sklearn.svm import SVC
from torch.nn.functional import softmax
from transformers import BertTokenizer, RobertaTokenizer
from collections import Counter

#load BERT model
bert_model = torch.load('/kaggle/input/bert_model/pytorch/model_full/1/model_full.pth')

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

#load roBERTa model

roberta_model = torch.load('/kaggle/input/roberta/pytorch/roberta/1/model_full.pth')

tokenizer_r = RobertaTokenizer.from_pretrained('roberta-base')

#load SVM model
with open('/kaggle/input/neutral_model/scikitlearn/neutral/1/neutral_model.sav', 'rb') as f:
    svm_neutral_model = pickle.load(f)
with open('/kaggle/input/pos_neg_model/scikitlearn/pos_neg/1/pos_neg_model.sav', 'rb') as f:
    svm_opinion_model = pickle.load(f)
#svm_neutral_model = pickle.load(('/kaggle/input/neutral_model/scikitlearn/neutral/1/neutral_model.sav', 'rb'))
#svm_opinion_model = pickle.load(('/kaggle/input/pos_neg_model/scikitlearn/pos_neg/1/pos_neg_model.sav', 'rb'))

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

    check_neutrality = svm_neutral_model.predict_proba([input_text])[0]
    

    best_confidence = max(check_neutrality)
    svm_sentiment = np.argmax(check_neutrality)
    
    check_polarity = svm_opinion_model.predict_proba([input_text])[0]
    polarity_confidence = max(check_polarity)
    
    if svm_sentiment == 0:
        svm_sentiment = 1
        svm_confidence = best_confidence
    
    else:
        if np.argmax(check_polarity) == 0:
            svm_sentiment = 0
        else:
            svm_sentiment = 2
        svm_confidence = polarity_confidence
    svm_con_arr = [check_polarity[0],check_neutrality[0],check_polarity[1]]



    #Final sentiment and Final Confidence
    predictions = [bert_sentiment, roberta_sentiment]
    count = Counter(predictions)
    final_sentiment, num_occurrences = count.most_common(1)[0]

    # Check if there is a majority
    if num_occurrences == 1:
        #print("FLAG 1")
        #SVM is used as tiebreaker
        if svm_sentiment in predictions:
            final_sentiment = svm_sentiment
            final_confidence = (probs[0, final_sentiment].item() + roberta_probs[0, final_sentiment].item() + svm_con_arr[final_sentiment]) /3
        #If still tie, roBERTa is used as the final sentiment
        else:
            final_sentiment = roberta_sentiment
            final_confidence = (probs[0, final_sentiment].item() + roberta_probs[0, final_sentiment].item()) /2
    else:
        #print("FLAG 2")
        final_sentiment = final_sentiment
        final_confidence = (probs[0, final_sentiment].item() + roberta_probs[0, final_sentiment].item()) /2

    labels = ['Negative', 'Neutral', 'Positive']  # Decode the predicted class index back to the label

    return [labels[final_sentiment], final_confidence]

# print(sentiment_output("Meta announces highest earnings"))

# print(sentiment_output("Meta announces lowest earnings"))

# print(sentiment_output("Meta announces earnings"))

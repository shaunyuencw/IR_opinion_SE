import torch
import pickle
import numpy as np
from sklearn.svm import SVC
from torch.nn.functional import softmax
from transformers import BertTokenizer, BertForSequenceClassification

#load BERT model
bert_model = torch.load('/bert_train/model_full.pth')

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

#load SVM model
svm_pn_model = pickle.load(('positive_model.sav', 'rb'))
svm_nn_model = pickle.load(('negative_model.sav', 'rb'))

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

    # Decode the predicted class index back to the label
    labels = ['Negative', 'Neutral', 'Positive']

    #Get BERT sentiment and confidence
    bert_sentiment = predicted_class
    bert_confidence = probs[0, predicted_class].item()

    #SVM PREDICTION

    if bert_sentiment == 2:
        prob_list = svm_pn_model.predict_proba(input_text)[0]
        svm_confidence = max(prob_list)
        svm_sentiment = prob_list.index(svm_confidence) + 1 #Shift 1 to get correct sentiment classification index

    elif bert_sentiment == 0:
        prob_list = svm_nn_model.predict_proba(input_text)[0]
        svm_confidence = max(prob_list)
        svm_sentiment = prob_list.index(svm_confidence)
    
    else:
        check_pos = svm_pn_model.predict_proba(input_text)[0]
        check_neg = svm_nn_model.predict_proba(input_text)[0]

        pos_confidence = max(check_pos)
        pos_sentiment = prob_list.index(pos_confidence) + 1 #Shift 1 to get correct sentiment classification index

        neg_confidence = max(check_neg)
        neg_sentiment = prob_list.index(neg_confidence)

        if pos_sentiment == neg_sentiment:
            svm_sentiment = 1
        elif pos_sentiment == 2 and neg_sentiment == 0:
            svm_sentiment = 1
        elif pos_sentiment == 2 and neg_sentiment == 1:
            svm_sentiment = 2
        else:
            svm_sentiment = 0

        svm_confidence = check_pos[0] *0.5 + check_neg[1] * 0.5
        




    #Final sentiment
    final_sentiment = round(bert_sentiment * 0.6 + svm_sentiment * 0.4)

    #Final confidence
    final_confidence = bert_confidence * 0.6 + svm_confidence * 0.4

    labels = ['Negative', 'Neutral', 'Positive']  # Decode the predicted class index back to the label

    return [labels[final_sentiment], final_confidence]

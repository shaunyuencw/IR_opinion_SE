import response_info_goog

datas = response_info_goog.data["news"]
numerator, denominator = 0, 0
positive, negative = 0, 0
for data in datas:
    sentiment, confidence = data["sentiment"]["sentiment"], data["sentiment"]["confidence"]
    if sentiment == "Positive":
        numerator += (1 * confidence)
        denominator += confidence
        positive += 1
    elif sentiment == "Negative":
        numerator += (-1 * confidence)
        denominator += confidence
        negative += 1

print(f"Positive {positive} : Negative {negative}")
sentiment_score = numerator / denominator
print("\tSentimental Score: ", sentiment_score)

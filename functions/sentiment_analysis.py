from textblob import TextBlob

def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def label_sentiment(score, threshold=0.2):
    if score > threshold:
        return 'Positive'
    elif score < 0:
        return 'Negative'
    else:
        return 'Neutral'

import pandas as pd

def load_dataset(csv_file_path):
    return pd.read_csv(csv_file_path, encoding='utf-8')

dataset = load_dataset('cleaned_file.csv')

# 1. Number of rows
num_rows = dataset.shape[0]

# 2. Number of unique topics
num_unique_topics = dataset['topic'].nunique()

# 3. Number of unique sources
num_unique_sources = dataset['source'].nunique()

# 4. Number of words
# Splitting each article by spaces to approximate word counts
num_words = dataset['article'].apply(lambda x: len(str(x).split())).sum()

# 5. Number of unique words
# Creating a set of all words to find unique words
all_words = set(word for article in dataset['article'] for word in str(article).split())
num_unique_words = len(all_words)

print(f"Number of rows: {num_rows}")
print(f"Number of unique topics: {num_unique_topics}")
print(f"Number of unique sources: {num_unique_sources}")
print(f"Number of words: {num_words}")
print(f"Number of unique words: {num_unique_words}")

# Count the number of each sentiment type
sentiment_counts = dataset['sentiments'].value_counts()

print(sentiment_counts)
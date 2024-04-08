import pandas as pd
from itertools import combinations

def load_dataset(csv_file_path):
    return pd.read_csv(csv_file_path, encoding='utf-8')

def cohen_kappa(rater1, rater2):
    assert len(rater1) == len(rater2), "Rater series must have the same length."
    
    # Calculate observed agreement
    agreement = sum(rater1 == rater2)
    p_o = agreement / len(rater1)
    
    # Calculate expected agreement
    rater1_counts = rater1.value_counts(normalize=True)
    rater2_counts = rater2.value_counts(normalize=True)
    p_e = sum(rater1_counts.get(cat, 0) * rater2_counts.get(cat, 0) for cat in set(rater1) | set(rater2))
    
    # Calculate Cohen's Kappa
    kappa = (p_o - p_e) / (1 - p_e)
    return kappa

def calc_dataset_kappa(dataset, annotator_columns):
    kappa_scores = []
    
    # Generate all combinations of pairs of annotators
    for annotator_pair in combinations(annotator_columns, 2):
        kappa_score = cohen_kappa(dataset[annotator_pair[0]], dataset[annotator_pair[1]])
        kappa_scores.append(kappa_score)
        print(f"Cohen's Kappa between {annotator_pair[0]} and {annotator_pair[1]}: {kappa_score:.3f}")
    
    # Calculate average Cohen's Kappa
    average_kappa = sum(kappa_scores) / len(kappa_scores)
    return average_kappa

dataset = load_dataset('test_set.csv')

# Calculate Cohen's Kappa between annotators
annotator_columns = ['annotator_1', 'annotator_2', 'annotator_3']
average_kappa = calc_dataset_kappa(dataset, annotator_columns)

print(f"\nAverage Cohen's Kappa: {average_kappa:.3f}")

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
sentiment_counts = dataset['majority'].value_counts()

print(sentiment_counts)
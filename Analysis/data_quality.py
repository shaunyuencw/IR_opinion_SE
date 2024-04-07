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
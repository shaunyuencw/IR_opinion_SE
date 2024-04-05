import pandas as pd

def load_dataset(csv_file_path):
    return pd.read_csv(csv_file_path, encoding='utf-8')

def get_dataset_column(dataset, column):
    return dataset[column].unique()

def filter_dataset(dataset, column, value):
    return dataset[dataset[column] == value]

def get_random_row(dataset):
    return dataset.sample(1)

csv_file_path = 'data/cleaned_file.csv'

# Load the CSV file into a pandas DataFrame
dataset = pd.read_csv(csv_file_path, encoding='utf-8', encoding_errors='replace')

# Get unique values in the 'search_query' column
unique_search_queries = get_dataset_column(dataset, 'topic')

# Let user choose a search query
# Print Topics with index for user to choose from
print("Topics")
for index, topic in enumerate(unique_search_queries):
    print(f"({index + 1}) {topic}")

while(True):
    search_index = input(f"\nChoose a topic index: (1-{len(unique_search_queries)}) (q to quit): ")
    if search_index == "q":
        break

    search_query = unique_search_queries[int(search_index) - 1]

    filtered_df = filter_dataset(dataset, 'topic', search_query)
    
    print(f"Showing 3 samples")
    for i in range(3):
        # Get a random row from the filtered DataFrame
        random_row = get_random_row(filtered_df)
        print(f"Topic: {random_row['topic'].values[0]}")
        print(f"Article: {random_row['article'].values[0]}")
        print(f"Source: {random_row['source'].values[0]}")
        print(f"Link: {random_row['article_link'].values[0]}")
        print(f"Sentiments: {random_row['sentiments'].values[0]}")

    # Summary of the filtered DataFrame
    print(f"\nSummary of {search_query}")
    # Count number of rows with each sentiment type
    print(f"Positive: {filtered_df[filtered_df['sentiments'] == 'positive'].shape[0]}")
    print(f"Negative: {filtered_df[filtered_df['sentiments'] == 'negative'].shape[0]}")
    print(f"Neutral: {filtered_df[filtered_df['sentiments'] == 'neutral'].shape[0]}")


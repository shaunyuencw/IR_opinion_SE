import pandas as pd
import re

def clean_article_text(text):
    if pd.isna(text):
        return ''

    text = str(text)
    
    # Remove leading/trailing whitespace
    text = text.replace('Cleaned Article Text', '')
    text = text.replace('Cleaned Article', '')
    text = text.replace('\u2019', '\'')  # Modified: ‚Äô
    text = text.replace('\u2018', '\'')  # Modified: ‚Äò
    text = text.replace('\u2013', '-')   # Modified: ‚Äì
    text = text.replace('\u201C', '"')  # Replace “ with "
    text.replace('\u201D', '"')  # Replace ” with "


    # Remove all newline characters
    text = re.sub(r'\\n|\*|^##\s*', ' ', text)

    # Remove asterisks and other special characters
    text = re.sub(r'[*]+', '', text)

    # Remove extra whitespace between words
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# Read the CSV file into a DataFrame
df = pd.read_csv('data/backup.csv')

# Apply the clean_article_text function to the 'article' column
df['article'] = df['article'].apply(clean_article_text)
df['title'] = df['title'].apply(clean_article_text)

# Save the updated DataFrame back to a CSV file
df.to_csv('data/cleaned_file.csv', index=False)

# IR Opinion SE Project - Backend

This project focuses on scraping web content and analyzing it for sentiment and opinions. It utilizes external APIs for data retrieval and analysis.

## Getting Started

These instructions will guide you through setting up the project on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have the following installed:

-   Anaconda or Miniconda
-   Git

### Setting Up the Environment
    
1.  **Create a Conda Environment**
    
    Create a new Conda environment with Python 3.x. Replace `your_env_name` with a name of your choice for the environment.
    `conda create --name news_api` 
    
    Activate the newly created environment:
    `conda activate your_env_name` 
    
2.  **Install Required Packages**
    
    Install the required Python packages within this environment.
    `pip install -r requirements.txt` 
    
3.  **Obtain an API Key from Serper API**
    
    -   Visit [Serper Dev API](https://serpapi.com/dashboard/) and sign up or log in to access the API section.
    -   Generate a new API key. Store this key securely as you will need it for accessing the API.
4.  Obtain an API Key from Google  LLM
    -   Visit [Google LLM](https://ai.google.dev/) and sign up or log in to access the API section.
    -   Generate a new API key. Store this key securely as you will need it for accessing the API.
5.  **Configure Your API Key**
    
    In the root directory of the project, create a `.env` file to securely store your API key.
    - `PALM2_API_TOKEN: "YOUR_API_KEY_HERE"` 
    -  `SERPER_DEV: "YOUR_API_KEY_HERE"` 
    
    Ensure to replace `YOUR_API_KEY_HERE` with your actual API key from serper.dev.
    

### Start the ElasticSearch Server
`docker compose up -d`

### Running the Application
With the environment set up and the API key configured, you're ready to run the application.

Start the server with `uvicorn backend:app --reload`


### Model:
1.  Berd 
2.  roBERTa  
3.  SVM
4.  LSTM (not in use)




### Appendix: Elastic search supporting features:
1. Basic Search Query: This searches for "Apple" in the Ticker and Name fields.
   - `GET http://localhost:8000/query/?search_term=Apple&exact_phrase=Apple Inc`
2. Exact Phrase Search: This searches for the exact phrase "Apple Inc" in the Name field.
   - `GET http://localhost:8000/query/?search_term=Apple&exact_phrase=Apple Inc`
1. Include Words: This searches for "micro" in the Name field and includes "software" and "hardware" in the Name field.
   - `GET http://localhost:8000/query/?search_term=micro&include_words=software&include_words=hardware`
1. Exclude Words: This searches for "energy" but excludes any results that have "solar" in the Name field.
   - `GET http://localhost:8000/query/?search_term=energy&exclude_words=solar`
1. Filter by Exchange Type: This searches for "financial" in companies listed on the NYSE.
   - `GET http://localhost:8000/query/?search_term=financial&exchange_type=NYSE`
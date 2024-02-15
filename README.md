
# IR Opinion SE Project

This project focuses on scraping web content and analyzing it for sentiment and opinions. It utilizes external APIs for data retrieval and analysis.

## Getting Started

These instructions will guide you through setting up the project on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have the following installed:

-   Anaconda or Miniconda
-   Git

### Setting Up the Environment

1.  **Clone the Repository**
    
    First, clone the repository to your local machine.
    `git clone https://github.com/shaunyuencw/IR_opinion_SE.git`
    `cd IR_opinion_SE` 
    
2.  **Create a Conda Environment**
    
    Create a new Conda environment with Python 3.x. Replace `your_env_name` with a name of your choice for the environment.
    `conda create --name news_api python=3.8` 
    
    Activate the newly created environment:
    `conda activate your_env_name` 
    
3.  **Install Required Packages**
    
    Install the required Python packages within this environment.
    `pip install -r requirements.txt` 
    
4.  **Obtain an API Key from serper.dev**
    
    -   Visit [serper.dev](https://serper.dev/) and sign up or log in to access the API section.
    -   Generate a new API key. Store this key securely as you will need it for accessing the API.
5.  **Configure Your API Key**
    
    In the root directory of the project, create a `config.yaml` file to securely store your API key.
    `api_key: "YOUR_API_KEY_HERE"` 
    
    Ensure to replace `YOUR_API_KEY_HERE` with your actual API key from serper.dev.
    

### Running the Application
With the environment set up and the API key configured, you're ready to run the application.
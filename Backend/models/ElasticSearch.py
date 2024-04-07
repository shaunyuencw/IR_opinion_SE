import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from typing import Optional, List
import json


class Elastic:
    def __init__(self):
        # Elasticsearch connection settings
        self.username = "elastic"
        self.password = "password"

        # Create Elasticsearch connection with authentication
        self.es = Elasticsearch(
            "http://localhost:9200",
            basic_auth=[self.username, self.password],
            verify_certs=False,
        )
        # Index name
        self.index_name = "stock_index"

    def load_data(self) -> None:
        # Read CSV file into a DataFrame
        csv_file_path = "../data/stock_info.csv"
        df = pd.read_csv(csv_file_path)
        print(f"Number of rows in the csv: {len(df)}")

        # Convert DataFrame to JSON with orient='records'
        json_data = df.to_json(orient="records")

        # Convert JSON data to a list of dictionaries
        documents = json.loads(json_data)

        # Use the bulk API to index the data
        actions = [
            {"_op_type": "index", "_index": self.index_name, "_source": doc}
            for doc in documents
        ]

        success, failed = bulk(self.es, actions)

        print(
            f"Successfully indexed {success} documents. Failed to index {failed} documents."
        )

    def perform_search(self, search_term: str, exact_phrase: Optional[str] = None, 
                       include_words: Optional[List[str]] = None, exclude_words: Optional[List[str]] = None, 
                       exchange_type: Optional[str] = None) -> list:
        if not search_term:
            return []

        # Basic multi_match query setup
        query = {
            "bool": {
                "must": [],
                "should": [
                    {"multi_match": {"query": search_term, "fields": ["Ticker", "Name"], "fuzziness": "AUTO"}}
                ],
                "must_not": [],
                "filter": []
            }
        }
        
        # Add exact phrase condition
        if exact_phrase:
            query['bool']['must'].append({"match_phrase": {"Name": exact_phrase}})

        # Add words to include
        if include_words:
            for word in include_words:
                query['bool']['must'].append({"match": {"Name": word}})

        # Add words to exclude
        if exclude_words:
            for word in exclude_words:
                query['bool']['must_not'].append({"match": {"Name": word}})
        
        # Filter by exchange type
        if exchange_type:
            query['bool']['filter'].append({"term": {"Exchange": exchange_type}})

        # Execute the search query
        search_results = self.es.search(index=self.index_name, body={"size": 10, "query": query})

        # Process results
        matching_symbols = []
        for hit in search_results['hits']['hits']:
            # if exchange_type and hit["_source"]["Exchange"] != exchange_type:
            #     continue
            item = {"symbol": hit["_source"]["Ticker"], "name": hit["_source"]["Name"]}
            matching_symbols.append(item)

        return matching_symbols



# elastic = Elastic()
# Load data into Elasticsearch
# elastic.load_data()

# Test search
# print("Query : {}\nResult: {}\n".format("App", elastic.perform_search("App")))
# print("Query : {}\nResult: {}\n".format("Tes", elastic.perform_search("Tes")))
# print("Query : {}\nResult: {}\n".format("Tesla", elastic.perform_search("Tesla")))
# print("Query : {}\nResult: {}\n".format("Goog", elastic.perform_search("Goog")))
# print("Query : {}\nResult: {}\n".format("Google", elastic.perform_search("Google")))
# print("Query : {}\nResult: {}\n".format("Goggle", elastic.perform_search("Goggle")))

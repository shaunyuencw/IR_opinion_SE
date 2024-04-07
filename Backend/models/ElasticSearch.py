import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
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

    def perform_search(self, search_term) -> list:
        if not search_term:
            return []

        # query top 10 hits with fuzziness
        q = {
            "size": 10,  # Limit the results to top 10 matches
            "query": {"multi_match": {"query": search_term, "fields": ["Ticker", "Name"], "fuzziness": "AUTO"}},
            
            # Query on a single field with fuzziness is not as accurate as multi_match
            # "query": {"match": {"Ticker": {"query": search_term, "fuzziness": "AUTO"}}},
        }
        search_results = self.es.search(index=self.index_name, body=q)

        matching_symbols = []
        for hit in search_results["hits"]["hits"]:
            # CSV Header : Ticker	Name	Exchange
            item = {
                "symbol": hit["_source"]["Ticker"],
                "name": hit["_source"]["Name"],
                }

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

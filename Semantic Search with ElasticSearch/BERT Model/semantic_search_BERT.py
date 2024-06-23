import torch
import numpy as np
from transformers import BertTokenizer, BertModel
from elasticsearch import Elasticsearch
import os

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")

# Initialize BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Function to encode query
def encode_query(query):
    inputs = tokenizer(query, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding

# Function to search documents
def search(query, threshold=1.5, top_k=5):
    query_vector = encode_query(query)
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }
    response = es.search(
        index="documents",
        body={
            "size": top_k,
            "query": script_query,
            "_source": {"includes": ["filename", "text"]}
        }
    )
    results = response['hits']['hits']
    filtered_results = [res for res in results if res['_score'] >= threshold]
    return filtered_results

# Function to read queries from a file
def read_queries(file_path):
    with open(file_path, 'r') as file:
        queries = file.readlines()
    return [query.strip() for query in queries]

# Function to format and display results
def display_results(query, results):
    print(f"\nQuery: {query}\n{'='*50}\n")
    if results:
        for idx, result in enumerate(results, 1):
            print(f"Result {idx}:\nFilename: {result['_source']['filename']}\nText: {result['_source']['text'][:200]}...\nScore: {result['_score']:.2f}\n{'-'*50}\n")
    else:
        print("No results found.")
    print("\n" + "="*50 + "\n")

# Main
if __name__ == "__main__":
    queries_file = "queries.txt"
    
    if os.path.exists(queries_file):
        queries = read_queries(queries_file)
        for query in queries:
            results = search(query)
            display_results(query, results)
    else:
        print(f"The file '{queries_file}' does not exist.")

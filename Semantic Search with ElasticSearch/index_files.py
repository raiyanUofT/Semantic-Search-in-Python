import os
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Define the index name
index_name = 'documents'

# Delete the index if it exists
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)

# Create index with mapping
mapping = {
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "text_vector": {"type": "dense_vector", "dims": 768}  # 768 dimensions for mpnet model
        }
    }
}
es.indices.create(index=index_name, body=mapping)

# Load the SentenceTransformer model
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Directory containing the text files
text_files_directory = 'text_files/'

# Index documents from text files
for i, filename in enumerate(os.listdir(text_files_directory)):
    if filename.endswith('.txt'):
        with open(os.path.join(text_files_directory, filename), 'r', encoding='utf-8') as file:
            text = file.read()
            try:
                vector = model.encode(text).tolist()
                doc = {"text": text, "text_vector": vector}
                es.index(index=index_name, id=i+1, body=doc)
                print(f"Indexed {filename}")
            except Exception as e:
                print(f"Error indexing {filename}: {e}")

print("Indexing completed.")
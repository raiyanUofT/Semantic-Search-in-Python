import os
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")

# Initialize SentenceTransformer model
model = SentenceTransformer('sentence-t5-base')

# Create index with the correct mapping
def create_index():
    if not es.indices.exists(index="documents"):
        es.indices.create(index="documents", body={
            "mappings": {
                "properties": {
                    "filename": {"type": "text"},
                    "text": {"type": "text"},
                    "embedding": {"type": "dense_vector", "dims": 768}
                }
            }
        })

# Load and encode documents
def encode_documents(folder_path):
    documents = []
    for filename in os.listdir(folder_path):
        with open(os.path.join(folder_path, filename), 'r') as file:
            text = file.read()
            embedding = model.encode(text).tolist()
            documents.append({
                '_index': 'documents',
                '_source': {
                    'filename': filename,
                    'text': text,
                    'embedding': embedding
                }
            })
    return documents

# Index documents
def index_documents(documents):
    bulk(es, documents)

# Main
if __name__ == "__main__":
    folder_path = "data/"
    create_index()
    documents = encode_documents(folder_path)
    index_documents(documents)
    print("Documents indexed successfully.")

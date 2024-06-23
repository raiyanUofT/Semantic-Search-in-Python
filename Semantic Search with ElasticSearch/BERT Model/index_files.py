import os
import torch
from transformers import BertTokenizer, BertModel
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")

# Initialize BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

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
            inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            documents.append({
                '_index': 'documents',
                '_source': {
                    'filename': filename,
                    'text': text,
                    'embedding': embedding.tolist()
                }
            })
    return documents

# Index documents
def index_documents(documents):
    bulk(es, documents)

# Main
if __name__ == "__main__":
    folder_path = "../text_files/"
    create_index()
    documents = encode_documents(folder_path)
    index_documents(documents)
    print("Documents indexed successfully.")

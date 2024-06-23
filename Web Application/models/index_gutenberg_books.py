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
                    "title": {"type": "text"},
                    "text": {"type": "text"},
                    "embedding": {"type": "dense_vector", "dims": 768}
                }
            }
        })

# Load and encode books
def encode_books(book_dir):
    documents = []
    for book_file in os.listdir(book_dir):
        book_path = os.path.join(book_dir, book_file)
        with open(book_path, 'r', encoding='utf-8') as file:
            text = file.read()
            title = os.path.splitext(book_file)[0]
            embedding = model.encode(text).tolist()
            documents.append({
                '_index': 'documents',
                '_source': {
                    'title': title,
                    'text': text,
                    'embedding': embedding
                }
            })
    return documents

# Index books
def index_books(documents):
    bulk(es, documents)

# Main
if __name__ == "__main__":
    book_dir = os.path.join("data", "books")  # Directory containing book text files
    create_index()
    documents = encode_books(book_dir)
    if documents:
        index_books(documents)
        print(f"Documents indexed successfully: {len(documents)} documents.")
    else:
        print("No documents to index.")

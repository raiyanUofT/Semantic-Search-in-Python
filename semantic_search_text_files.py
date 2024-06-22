import os
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load pre-trained SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Directory containing text files
text_dir = 'text_files'

# Read text files
documents = []
filenames = []
for filename in os.listdir(text_dir):
    if filename.endswith('.txt'):
        with open(os.path.join(text_dir, filename), 'r') as file:
            documents.append(file.read())
            filenames.append(filename)

# Encode documents using the model
document_embeddings = model.encode(documents)

# Function to perform semantic search
def semantic_search(query, top_k=3):
    query_embedding = model.encode(query)
    hits = util.semantic_search(query_embedding, document_embeddings, top_k=top_k)
    hits = hits[0]  # Get the first list of hits
    results = [(filenames[hit['corpus_id']], hit['score']) for hit in hits]
    return results

# Example query
query = "Tell me about proposals"
results = semantic_search(query)

# Print results
print(f"Query: {query}\n")
print("Top results:")
for filename, score in results:
    print(f"{filename}: {score:.4f}")
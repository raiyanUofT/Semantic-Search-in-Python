import os
import pandas as pd
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import numpy as np

# Initialize Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Define the index name
index_name = 'educational_materials'

# Delete the index if it exists
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)

# Create index with mapping
mapping = {
    "mappings": {
        "properties": {
            "content": {"type": "text"},
            "embedding": {"type": "dense_vector", "dims": 768}  # Update to match the embedding size of Sentence-T5
        }
    }
}
es.indices.create(index=index_name, body=mapping)

# Load the Sentence-T5 model
model = SentenceTransformer('sentence-transformers/sentence-t5-base')

# Load training data
df = pd.read_csv('training_data.csv')
train_examples = [InputExample(texts=[row['sentence1'], row['sentence2']], label=row['score']) for index, row in df.iterrows()]
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=8)
train_loss = losses.CosineSimilarityLoss(model)

# Fine-tune the model
model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=1, warmup_steps=100)

# Directory containing the text files
text_files_directory = '../text_files/'

# Index documents from text files
documents = []
for i, filename in enumerate(os.listdir(text_files_directory)):
    if filename.endswith('.txt'):
        with open(os.path.join(text_files_directory, filename), 'r', encoding='utf-8') as file:
            content = file.read()
            try:
                embedding = model.encode(content)
                normalized_embedding = embedding / np.linalg.norm(embedding)  # Normalize the embedding
                documents.append({
                    "_index": index_name,
                    "_source": {
                        "content": content,
                        "embedding": normalized_embedding.tolist()  # Convert to list for JSON serialization
                    }
                })
                print(f"Indexed {filename}")
            except Exception as e:
                print(f"Error indexing {filename}: {e}")

# Bulk index documents
helpers.bulk(es, documents)

print("Indexing completed.")

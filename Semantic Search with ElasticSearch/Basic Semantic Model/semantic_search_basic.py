from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

# Initialize Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Load the SentenceTransformer model
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Query text
query = "Computer Science"
query_vector = model.encode(query).tolist()

# Search request
response = es.search(index="documents", body={
    "query": {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'text_vector') + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }
})

# Print the results
for hit in response['hits']['hits']:
    print(f"Text: {hit['_source']['text']}, Score: {hit['_score']}")
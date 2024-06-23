from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")

# Initialize SentenceTransformer model
model = SentenceTransformer('sentence-t5-base')

# Function to encode query for semantic search
def encode_query(query):
    embedding = model.encode(query).tolist()
    return embedding

# Function to perform keyword search
def keyword_search(query, top_k=5):
    response = es.search(
        index="documents",
        body={
            "size": top_k,
            "query": {
                "match": {
                    "text": query
                }
            },
            "_source": {"includes": ["title", "text"]}
        }
    )
    results = response['hits']['hits']
    return results

# Function to perform semantic search
def semantic_search(query, top_k=5):
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
            "_source": {"includes": ["title", "text"]}
        }
    )
    results = response['hits']['hits']
    return results

# Function to normalize scores to be between 1 and 2
def normalize_scores(results):
    if not results:
        return results
    scores = [result['_score'] for result in results]
    min_score = min(scores)
    max_score = max(scores)
    if max_score == min_score:
        for result in results:
            result['_score'] = 1.0
    else:
        for result in results:
            result['_score'] = 1 + ((result['_score'] - min_score) / (max_score - min_score))
    return results

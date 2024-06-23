from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import ScriptScore
from sentence_transformers import SentenceTransformer

# Initialize Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Load the fine-tuned Sentence-T5 model
model = SentenceTransformer('sentence-transformers/sentence-t5-base')

# Function to perform semantic search
def semantic_search(query, model, es, index_name):
    query_embedding = model.encode(query).tolist()

    s = Search(using=es, index=index_name).query(
        ScriptScore(
            query={"match_all": {}},
            script={
                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                "params": {"query_vector": query_embedding}
            }
        )
    )

    response = s.execute()
    return [(hit.content, hit.meta.score) for hit in response]

# Example search query
results = semantic_search("Explain photosynthesis", model, es, "educational_materials")
for content, score in results:
    print(f"Score: {score}, Content: {content[:200]}...")

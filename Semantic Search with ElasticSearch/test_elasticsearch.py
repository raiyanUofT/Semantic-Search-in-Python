from elasticsearch import Elasticsearch

# Connect to the local Elasticsearch instance
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme':'http'}])

# Check if the connection was successful
if es.ping():
    print("Connected to ElasticSearch")
else:
    print("Could not connect to ElasticSearch")

# Create an index
es.indices.create(index='test-index', ignore=400)

# Index a document
doc = {
    'author': 'Reetseey',
    'text': 'Elasticsearch is cool!',
    'timestamp': '2024-06-23'
}
res = es.index(index='test-index', id=1, body=doc)
print(f"Indexed document: {res['result']}")

# Retrieve the document
res = es.get(index='test-index', id=1)
print(f"Retrieved document: {res['_source']}")

# Search the index
res = es.search(index='test-index', body={"query": {"match_all": {}}})
print("Search results:")
for hit in res['hits']['hits']:
    print(hit['_source'])
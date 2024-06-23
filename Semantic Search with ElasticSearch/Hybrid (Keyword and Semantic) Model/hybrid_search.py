from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from rich.console import Console
from rich.table import Table
from rich import box
import os

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")

# Initialize SentenceTransformer model
model = SentenceTransformer('sentence-t5-base')

# Initialize console for rich printing
console = Console()

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
            "_source": {"includes": ["filename", "text"]}
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
            "_source": {"includes": ["filename", "text"]}
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

# Function to decide which search to use
def decide_search(query):
    if len(query.split()) < 3 or "keyword:" in query:
        return "keyword"
    else:
        return "semantic"

# Function to read queries from a file
def read_queries(file_path):
    with open(file_path, 'r') as file:
        queries = file.readlines()
    return [query.strip() for query in queries]

# Function to format and display results using rich
def display_results(query, results, search_type):
    table = Table(title=f"[bold yellow]Query:[/bold yellow] {query} | [bold cyan]Search Type:[/bold cyan] {search_type}", box=box.ROUNDED)

    table.add_column("Rank", style="dim", width=6)
    table.add_column("Filename", style="green", min_width=20)
    table.add_column("Text", style="magenta", min_width=80)
    table.add_column("Score", style="bold blue", justify="right")

    if results:
        for idx, result in enumerate(results, 1):
            table.add_row(
                str(idx),
                result['_source']['filename'],
                result['_source']['text'][:200] + "...",
                f"{result['_score']:.2f}"
            )
    else:
        table.add_row("No results found.", "", "", "")

    console.print(table)

# Main
if __name__ == "__main__":
    queries_file = "queries.txt"
    
    if os.path.exists(queries_file):
        queries = read_queries(queries_file)
        for query in queries:
            search_type = decide_search(query)
            if search_type == "keyword":
                results = keyword_search(query.replace("keyword:", "").strip(), top_k=5)
                results = normalize_scores(results)
            else:
                results = semantic_search(query, top_k=5)
                results = normalize_scores(results)
            display_results(query, results, search_type)
    else:
        print(f"The file '{queries_file}' does not exist.")

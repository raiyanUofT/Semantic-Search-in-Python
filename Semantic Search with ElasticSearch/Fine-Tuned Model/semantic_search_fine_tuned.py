from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import ScriptScore
from sentence_transformers import SentenceTransformer
from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Initialize Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Load the fine-tuned Sentence-T5 model
model = SentenceTransformer('sentence-transformers/sentence-t5-base')

# Function to perform semantic search
def semantic_search(query, model, es, index_name, threshold=1.5, top_n=5):
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

    # Execute the search
    response = s.execute()
    
    # Filter results based on the threshold and get top N results
    results = [(hit.content, hit.meta.score) for hit in response if hit.meta.score >= threshold]
    results = results[:top_n]  # Return only the top N results or those above the threshold

    return query, results

# Function to pretty print results
def pretty_print_results(query, results):
    console = Console()
    console.print(Panel(f"[bold magenta]Query:[/bold magenta] {query}", border_style="bold cyan"))
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="dim", width=6)
    table.add_column("Score", justify="right")
    table.add_column("Content")

    for i, (content, score) in enumerate(results, start=1):
        table.add_row(str(i), f"{score:.2f}", content[:200] + "...")

    console.print(table)

# Read queries from the file
def read_queries_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        queries = [line.strip() for line in file if line.strip()]
    return queries

# File containing the user queries
queries_file = 'queries.txt'

# Read queries from file
queries = read_queries_from_file(queries_file)

# Process each query and display results
for query in queries:
    query, results = semantic_search(query, model, es, "educational_materials")
    pretty_print_results(query, results)

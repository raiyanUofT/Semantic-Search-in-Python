import os
import xml.etree.ElementTree as ET
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")

# Initialize SentenceTransformer model
model = SentenceTransformer('sentence-t5-base')

# Define the index name
index_name = 'documents'

# Delete the index if it exists
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)

# Create index with the correct mapping
def create_index():
    if not es.indices.exists(index="documents"):
        es.indices.create(index="documents", body={
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "summary": {"type": "text"},
                    "embedding": {"type": "dense_vector", "dims": 768}
                }
            }
        })

# Load and encode documents
def encode_documents(file_path):
    documents = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        for record in root.findall(".//{http://www.openarchives.org/OAI/2.0/}record"):
            metadata = record.find("{http://www.openarchives.org/OAI/2.0/}metadata")
            
            if metadata is not None:
                dc_metadata = metadata.find(".//{http://www.openarchives.org/OAI/2.0/oai_dc/}dc")
                if dc_metadata is not None:
                    title_element = dc_metadata.find("{http://purl.org/dc/elements/1.1/}title")
                    description_elements = dc_metadata.findall("{http://purl.org/dc/elements/1.1/}description")
                    
                    if title_element is not None and description_elements:
                        title = title_element.text
                        summary = " ".join(desc.text for desc in description_elements if desc.text)
                        
                        if title and summary:  # Ensure neither is None or empty
                            text = f"{title}. {summary}"
                            embedding = model.encode(text).tolist()
                            documents.append({
                                '_index': 'documents',
                                '_source': {
                                    'title': title,
                                    'summary': summary,
                                    'embedding': embedding
                                }
                            })
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
    return documents

# Index documents
def index_documents(documents):
    bulk(es, documents)

# Main
if __name__ == "__main__":
    file_path = os.path.join("data", "arxiv_data.xml")  # Ensure the file path is correct
    if os.path.exists(file_path):
        create_index()
        documents = encode_documents(file_path)
        if documents:
            index_documents(documents)
            print(f"Documents indexed successfully: {len(documents)} documents.")
        else:
            print("No documents to index.")
    else:
        print(f"XML file not found at {file_path}. Please check the path and try again.")

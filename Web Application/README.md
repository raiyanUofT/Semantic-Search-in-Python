# Search Engine with Flask and Elasticsearch

This project demonstrates how to implement a search engine with both keyword and semantic search capabilities using Flask, Elasticsearch, and SentenceTransformers. The web interface allows users to choose between keyword search, semantic search, or both, and displays the results in a user-friendly format.

## Prerequisites

- Python 3.10
- Elasticsearch 7.10 or higher

## Setup Instructions

### 1. Install Elasticsearch

1. **Download and Install Elasticsearch:**
    ```bash
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.10.2-amd64.deb
    sudo dpkg -i elasticsearch-7.10.2-amd64.deb
    ```

2. **Start Elasticsearch:**
    ```bash
    sudo systemctl start elasticsearch
    sudo systemctl enable elasticsearch
    ```

3. **Verify Elasticsearch is Running:**
    Open your browser and navigate to `http://localhost:9200`. You should see a JSON response from Elasticsearch.

4. **TO BE UPDATED**
This project demonstrates simple semantic search with ElasticSearch. It has been tested on Ubuntu 22.04 LTS and Python 3.10.12.

New text files can be added to the 'text_files/' directory. 
The query that is being searched can be altered in the 'semantic_search_with_elasticsearch.py' file.

Steps to run the program:

1- Install the dependencies in requirements.txt by typing the following in terminal: pip install -r requirements.txt

2- Run the script semantic_search_with_elasticsearch.py

3- Results will show a list of documents (with their content) that match the query semantically,
along with a confidence score for each matched document.

OPTIONAL

4- To test if Elasticsearch is working, run the script test_elasticsearch.py. 
If ElasticSearch has been correctly installed and started, there should be output indicating that 
the connection to ElasticSearch was successful, a document was indexed, and the document was retrieved 
and searched.

5- To test semantic search without using ElasticSearch, run the python script test_semantic_search.py.
The query can be modified inside the script. For details, look at the 'Semantic Search with Text Files' 
directory.

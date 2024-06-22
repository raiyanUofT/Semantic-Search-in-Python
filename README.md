This project demonstrates simple semantic search on text files. New text files can be added to the 'text_files/' directory.
The query that is being searched can be altered in the 'semantic_search.py' file. Currently, the top 3 documents are displayed in the
results. This can also be changed by modifying the 'top_k' parameter in the 'semantic_search' function.

Steps to run the program:

1- Install the dependencies in requirements.txt by typing the following in terminal: 
   pip install -r requirements.txt

2- Run the script semantic_search.py

3- Results will show a list of documents that match the query semantically. along with a confidence score for each matched document

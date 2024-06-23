from flask import render_template, request, session
from app import app
from models.search import keyword_search, semantic_search, normalize_scores
import uuid

# Configure secret key for sessions
app.secret_key = str(uuid.uuid4())

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'history' not in session:
        session['history'] = []
    
    if request.method == 'POST':
        query = request.form['query']
        search_type = request.form['search_type']
        results = []
        unique_docs = set()

        if search_type == 'keyword':
            keyword_results = keyword_search(query)
            keyword_results = normalize_scores(keyword_results)
            for result in keyword_results:
                if result['_source']['filename'] not in unique_docs:
                    unique_docs.add(result['_source']['filename'])
                    results.append(result)
        elif search_type == 'semantic':
            semantic_results = semantic_search(query)
            semantic_results = normalize_scores(semantic_results)
            for result in semantic_results:
                if result['_source']['filename'] not in unique_docs:
                    unique_docs.add(result['_source']['filename'])
                    results.append(result)

        # Sort results by score in descending order
        results = sorted(results, key=lambda x: x['_score'], reverse=True)[:5]

        # Add query to history
        session['history'].append({'query': query, 'search_type': search_type})
        session.modified = True

        return render_template('index.html', query=query, results=results, search_type=search_type, history=session['history'])
    
    return render_template('index.html', history=session['history'])

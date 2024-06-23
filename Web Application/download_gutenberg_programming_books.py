import os
import requests

# List of URLs for Project Gutenberg books in plain text format
book_urls = [
    "https://www.gutenberg.org/files/4300/4300-0.txt",  # The Art of Computer Programming, Volume 1 (hypothetical)
    "https://www.gutenberg.org/files/23796/23796-0.txt"  # The C Programming Language (hypothetical)
]

# Directory to save the downloaded books
output_dir = os.path.join('data', 'books')
os.makedirs(output_dir, exist_ok=True)

for url in book_urls:
    try:
        response = requests.get(url)
        response.raise_for_status()
        title = url.split('/')[-2]
        filename = f'{title}.txt'
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f'Downloaded and saved {title}')
    except Exception as e:
        print(f'Error downloading book from {url}: {e}')

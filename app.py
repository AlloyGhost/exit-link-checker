from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

# Rate limiter: 10 requests per minute per IP
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"]
)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme in ["http", "https"], result.netloc])
    except:
        return False

def extract_exit_links(url):
    try:
        domain = url.split('/')[2]
        html = requests.get(url, timeout=5).text
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http') and domain not in href:
                links.append(href)
        return list(set(links))
    except Exception as e:
        return [f"Error: {str(e)}"]

@app.route('/api/exit-links', methods=['POST'])
@limiter.limit("10 per minute")
def get_exit_links():
    data = request.get_json()
    url = data.get('url')

    # ✅ Validate the URL format
    if not url or not is_valid_url(url):
        return jsonify({"error": "Invalid or missing URL"}), 400

    links = extract_exit_links(url)
    return jsonify({"links": links})

@app.route('/')
def home():
    return "Exit Link Checker API is live!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host='0.0.0.0', port=port)

"""
Price Tracker Local Server
Serves the UI and provides API to read/write price_watchlist.json directly.

Run:  python pricetracker/server.py
Open: http://localhost:5050
"""

from flask import Flask, request, jsonify, send_file
import json, os, sys

app = Flask(__name__)

WATCHLIST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scrapers', 'price_watchlist.json')
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scrapers', 'price_history.json')
MAX_PRODUCTS = 5


@app.route('/')
def index():
    return send_file('index.html')


@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """Read the watchlist JSON."""
    if not os.path.exists(WATCHLIST_FILE):
        return jsonify({"products": []})
    with open(WATCHLIST_FILE) as f:
        return jsonify(json.load(f))


@app.route('/api/watchlist', methods=['POST'])
def save_watchlist():
    """Save the entire watchlist JSON."""
    data = request.json
    if not data or 'products' not in data:
        return jsonify({"error": "Invalid data"}), 400

    products = data['products']
    if len(products) > MAX_PRODUCTS:
        return jsonify({"error": f"Max {MAX_PRODUCTS} products allowed"}), 400

    with open(WATCHLIST_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    return jsonify({"status": "saved", "count": len(products)})


@app.route('/api/history', methods=['GET'])
def get_history():
    """Read the price history JSON."""
    if not os.path.exists(HISTORY_FILE):
        return jsonify({})
    with open(HISTORY_FILE) as f:
        return jsonify(json.load(f))


if __name__ == '__main__':
    print("=" * 50)
    print("  Price Tracker — Local Server")
    print("=" * 50)
    print(f"  Watchlist: {os.path.abspath(WATCHLIST_FILE)}")
    print(f"  UI: http://localhost:5050")
    print("=" * 50)
    app.run(host='127.0.0.1', port=5050, debug=False)

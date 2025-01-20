from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from pymongo import MongoClient
from bson import ObjectId
import os

app = Flask(__name__)
CORS(app)

# Swagger setup
SWAGGER_URL = '/swagger'
API_URL = '/static/authors.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={'app_name': "Authors Service API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# MongoDB setup
MONGO_URI = 'mongodb+srv://username:password@your-cluster-url'  # Replace with your MongoDB URI
client = MongoClient(MONGO_URI)
db = client['library']  # database name
authors_collection = db['authors']  # collection name

@app.route('/authors', methods=['GET'])
def get_all_authors():
    """Get all authors."""
    authors = list(authors_collection.find({}, {'_id': 0}))  # Exclude MongoDB _id
    return jsonify(authors)

@app.route('/authors/<author_name>', methods=['GET'])
def get_author(author_name):
    """Get a specific author."""
    author = authors_collection.find_one({'name': author_name}, {'_id': 0})
    if author:
        return jsonify(author)
    return jsonify({"message": "Author not found"}), 404

@app.route('/authors', methods=['POST'])
def create_author():
    """Create a new author."""
    data = request.json
    if "name" not in data or "books" not in data:
        return jsonify({"error": "Invalid author data"}), 400
    
    # Check if author already exists
    if authors_collection.find_one({'name': data['name']}):
        return jsonify({"error": "Author already exists"}), 409
    
    authors_collection.insert_one(data)
    return jsonify({"message": "Author created", "author": data}), 201

@app.route('/authors/<author_name>/books', methods=['POST'])
def add_book_to_author(author_name):
    """Add a book to an existing author."""
    data = request.json
    if not data or 'title' not in data:
        return jsonify({"error": "Invalid book data"}), 400

    result = authors_collection.update_one(
        {'name': author_name},
        {'$push': {'books': data['title']}}
    )

    if result.modified_count:
        author = authors_collection.find_one({'name': author_name}, {'_id': 0})
        return jsonify({"message": "Book added to author", "author": author}), 200
    return jsonify({"message": "Author not found"}), 404

@app.route('/authors/<author_name>', methods=['PUT'])
def update_author(author_name):
    """Update an existing author."""
    data = request.json
    if "name" not in data or "books" not in data:
        return jsonify({"error": "Invalid author data"}), 400

    result = authors_collection.update_one(
        {'name': author_name},
        {'$set': data}
    )

    if result.modified_count:
        return jsonify({"message": "Author updated", "author": data}), 200
    return jsonify({"message": "Author not found"}), 404

@app.route('/authors/<author_name>', methods=['DELETE'])
def delete_author(author_name):
    """Delete an author."""
    result = authors_collection.delete_one({'name': author_name})
    if result.deleted_count:
        return jsonify({"message": "Author deleted"}), 200
    return jsonify({"message": "Author not found"}), 404

@app.route('/authors/<author_name>/books/<book_title>', methods=['DELETE'])
def delete_book_from_author(author_name, book_title):
    """Delete a book from an author's list."""
    result = authors_collection.update_one(
        {'name': author_name},
        {'$pull': {'books': book_title}}
    )

    if result.modified_count:
        author = authors_collection.find_one({'name': author_name}, {'_id': 0})
        return jsonify({"message": "Book removed from author", "author": author}), 200
    return jsonify({"message": "Author or book not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8012)
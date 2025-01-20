from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)

# Swagger setup
SWAGGER_URL = '/swagger'
API_URL = '/static/authors.yaml' # Create this YAML file
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={'app_name': "Authors Service API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

authors = {} # In-memory store


@app.route('/authors', methods=['GET'])
def get_all_authors():
    """Get all authors."""
    return jsonify(authors)


@app.route('/authors/<author_name>', methods=['GET'])
def get_author(author_name):
    """Get a specific author."""
    if author_name in authors:
       return jsonify(authors[author_name])
    return jsonify({"message": "Author not found"}), 404



@app.route('/authors', methods=['POST'])
def create_author():
    """Create a new author."""
    data = request.json
    if "name" not in data or "books" not in data: # Basic validation
      return jsonify({"error": "Invalid author data"}), 400
    authors[data["name"]] = data  # Add author to the dictionary
    return jsonify({"message": "Author created", "author": data}), 201



@app.route('/authors/<author_name>/books', methods=['POST'])
def add_book_to_author(author_name):
    """Add a book to an existing author."""

    data = request.json  # Expecting {'title': 'book_title'}

    if not data or 'title' not in data:
        return jsonify({"error": "Invalid book data"}), 400


    if author_name in authors:
        if "books" not in authors[author_name]:
            authors[author_name]["books"] = []  # Initialize if not present

        authors[author_name]["books"].append(data['title'])
        return jsonify({"message": "Book added to author", "author": authors[author_name]}), 200

    return jsonify({"message": "Author not found"}), 404


@app.route('/authors/<author_name>', methods=['PUT'])
def update_author(author_name):
    """Update an existing author."""

    data = request.json
    if "name" not in data or "books" not in data:
        return jsonify({"error": "Invalid author data"}), 400


    if author_name in authors:
        authors[author_name] = data # Update author information
        return jsonify({"message": "Author updated", "author": data}), 200
    return jsonify({"message": "Author not found"}), 404


@app.route('/authors/<author_name>', methods=['DELETE'])
def delete_author(author_name):
    if author_name in authors:
        del authors[author_name]
        return jsonify({"message": "Author deleted"}), 200
    return jsonify({"message": "Author not found"}), 404

@app.route('/authors/<author_name>/books/<book_title>', methods=['DELETE'])
def delete_book_from_author(author_name, book_title):

    if author_name in authors:
        if 'books' in authors[author_name] and book_title in authors[author_name]['books']:
            authors[author_name]['books'].remove(book_title) # Remove book from list
            return jsonify({"message": "Book removed from author", "author": authors[author_name]}), 200
        return jsonify({"message": "Book not found in author's list"}), 404
    return jsonify({"message": "Author not found"}), 404



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8012)
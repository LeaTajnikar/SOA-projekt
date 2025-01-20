from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)

# Swagger setup
SWAGGER_URL = '/swagger'
API_URL = '/static/genres.yaml'  # Create this file
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={'app_name': "Genres Service API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# In-memory genres storage
genres = {}

# Endpoint: Get all genres (GET)
@app.route('/genres', methods=['GET'])
def get_all_genres():
    return jsonify(genres), 200

# Endpoint: Get a specific genre (GET)
@app.route('/genres/<genre_name>', methods=['GET'])
def get_genre(genre_name):
    if genre_name in genres:
        return jsonify(genres[genre_name]), 200
    return jsonify({"message": "Genre not found"}), 404

# Endpoint: Create a new genre (POST)
@app.route('/genres', methods=['POST'])
def create_genre():
    data = request.json
    if 'name' not in data or 'description' not in data:
        return jsonify({"error": "Invalid genre data. 'name' and 'description' are required."}), 400

    genres[data['name']] = {
        "description": data['description'],
        "books": []
    }
    return jsonify({"message": "Genre created", "genre": genres[data['name']]}), 201

# Endpoint: Add a book to a genre (POST)
@app.route('/genres/<genre_name>/books', methods=['POST'])
def add_book_to_genre(genre_name):
    data = request.json
    if not data or 'title' not in data:
        return jsonify({"error": "Invalid book data. 'title' is required."}), 400

    if genre_name in genres:
        genres[genre_name].setdefault("books", []).append(data["title"])
        return jsonify({"message": "Book added to genre", "genre": genres[genre_name]}), 200

    return jsonify({"message": "Genre not found"}), 404

# Endpoint: Update a genre (PUT)
@app.route('/genres/<genre_name>', methods=['PUT'])
def update_genre(genre_name):
    data = request.json
    if 'name' not in data or 'description' not in data:
        return jsonify({"error": "Invalid genre data. 'name' and 'description' are required."}), 400

    if genre_name in genres:
        genres[genre_name] = {
            "description": data['description'],
            "books": genres[genre_name].get("books", [])
        }
        return jsonify({"message": "Genre updated", "genre": genres[genre_name]}), 200

    return jsonify({"message": "Genre not found"}), 404

# Endpoint: Delete a genre (DELETE)
@app.route('/genres/<genre_name>', methods=['DELETE'])
def delete_genre(genre_name):
    if genre_name in genres:
        del genres[genre_name]
        return jsonify({"message": "Genre deleted"}), 200

    return jsonify({"message": "Genre not found"}), 404

# Endpoint: Remove a book from a genre (DELETE)
@app.route('/genres/<genre_name>/books/<book_title>', methods=['DELETE'])
def remove_book_from_genre(genre_name, book_title):
    if genre_name in genres:
        if book_title in genres[genre_name].get("books", []):
            genres[genre_name]["books"].remove(book_title)
            return jsonify({"message": "Book removed from genre", "genre": genres[genre_name]}), 200
        return jsonify({"message": "Book not found in this genre"}), 404

    return jsonify({"message": "Genre not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8013)
# genres-service.py

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



genres = {}  # Use a dictionary to store genres


@app.route('/genres', methods=['GET'])
def get_all_genres():
    """Get all genres."""
    return jsonify(genres)


@app.route('/genres/<genre_name>', methods=['GET'])
def get_genre(genre_name):
    """Get a specific genre."""
    if genre_name in genres:
        return jsonify(genres[genre_name])  # Return genre details
    return jsonify({"message": "Genre not found"}), 404


@app.route('/genres', methods=['POST'])
def create_genre():
    """Create a new genre."""
    data = request.json
    if 'name' not in data or 'description' not in data:  # Check if required fields are present
        return jsonify({"error": "Invalid genre data. 'name' and 'description' are required."}), 400


    genres[data['name']] = data  # Add the genre to the dictionary
    return jsonify({"message": "Genre created", "genre": data}), 201  # Return 201 Created status



@app.route('/genres/<genre_name>/books', methods=['POST'])
def add_book_to_genre(genre_name):
    """Add a book to a genre."""
    data = request.json # Expecting {'title': 'book_title'}
    if not data or 'title' not in data:
        return jsonify({"error": "Invalid book data"}), 400

    if genre_name in genres:
        if "books" not in genres[genre_name]:
            genres[genre_name]["books"] = []

        genres[genre_name]["books"].append(data["title"])  # Assuming 'title' is the key for book titles
        return jsonify({"message": "Book added to genre", "genre": genres[genre_name]}), 200

    return jsonify({"message": "Genre not found"}), 404


@app.route('/genres/<genre_name>', methods=['PUT'])
def update_genre(genre_name):

    data = request.json
    if 'name' not in data or 'description' not in data:
        return jsonify({"error": "Invalid genre data. 'name' and 'description' are required."}), 400


    if genre_name in genres:
        genres[genre_name] = data # Update genre data
        return jsonify({"message": "Genre updated", "genre": data}), 200

    return jsonify({"message": "Genre not found"}), 404


@app.route('/genres/<genre_name>', methods=['DELETE'])
def delete_genre(genre_name):

    if genre_name in genres:
        del genres[genre_name]  # Delete the genre
        return jsonify({"message": "Genre deleted"}), 200

    return jsonify({"message": "Genre not found"}), 404


@app.route('/genres/<genre_name>/books/<book_title>', methods=['DELETE'])
def remove_book_from_genre(genre_name, book_title):
    """Remove a book from a genre."""
    if genre_name in genres:
        if 'books' in genres[genre_name] and book_title in genres[genre_name]['books']:
            genres[genre_name]['books'].remove(book_title) #Remove the book
            return jsonify({"message": "Book removed from genre", "genre": genres[genre_name]}), 200
        return jsonify({"message": "Book not found in this genre"}), 404 #Book doesn't exist
    return jsonify({"message": "Genre not found"}), 404




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8008) # Choose a different port
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from pymongo import MongoClient
from bson import ObjectId
import os
from graphene import ObjectType, String, List, Schema, Field
import graphene
from flask_graphql import GraphQLView

app = Flask(__name__)
CORS(app)

# Swagger setup
SWAGGER_URL = '/swagger'
API_URL = '/static/genres.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={'app_name': "Genres Service API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# MongoDB setup
MONGO_URI = 'mongodb+srv://username:password@your-cluster-url'  # Replace with your MongoDB URI
client = MongoClient(MONGO_URI)
db = client['library']  # database name
genres_collection = db['genres']  # collection name

# GraphQL Types

class GenreType(ObjectType):
    name = String()
    description = String()
    books = List(String)

class Query(ObjectType):
    # Query to get all genres
    all_genres = List(GenreType)
    # Query to get genre by name
    genre_by_name = Field(GenreType, name=String(required=True))

    def resolve_all_genres(self, info):
        genres = list(genres_collection.find({}, {'_id': 0}))
        return [GenreType(
            name=genre['name'],
            description=genre['description'],
            books=genre['books']
        ) for genre in genres]

    def resolve_genre_by_name(self, info, name):
        genre = genres_collection.find_one({'name': name}, {'_id': 0})
        if genre:
            return GenreType(
                name=genre['name'],
                description=genre['description'],
                books=genre['books']
            )
        return None

# GraphQL Schema
schema = Schema(query=Query)

# GraphQL route
app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql', schema=schema, graphiql=True))  # graphiql=True enables GraphiQL interface for testing queries

# REST API Routes

@app.route('/genres', methods=['GET'])
def get_all_genres():
    """Get all genres."""
    genres = list(genres_collection.find({}, {'_id': 0}))
    return jsonify(genres), 200

@app.route('/genres/<genre_name>', methods=['GET'])
def get_genre(genre_name):
    """Get a specific genre."""
    genre = genres_collection.find_one({'name': genre_name}, {'_id': 0})
    if genre:
        return jsonify(genre), 200
    return jsonify({"message": "Genre not found"}), 404

@app.route('/genres', methods=['POST'])
def create_genre():
    """Create a new genre."""
    data = request.json
    if 'name' not in data or 'description' not in data:
        return jsonify({"error": "Invalid genre data. 'name' and 'description' are required."}), 400
    
    # Check if genre already exists
    if genres_collection.find_one({'name': data['name']}):
        return jsonify({"error": "Genre already exists"}), 409
    
    new_genre = {
        "name": data['name'],
        "description": data['description'],
        "books": []
    }
    
    genres_collection.insert_one(new_genre)
    del new_genre['_id']  # Remove _id before returning
    return jsonify({"message": "Genre created", "genre": new_genre}), 201

@app.route('/genres/<genre_name>/books', methods=['POST'])
def add_book_to_genre(genre_name):
    """Add a book to a genre."""
    data = request.json
    if not data or 'title' not in data:
        return jsonify({"error": "Invalid book data. 'title' is required."}), 400

    result = genres_collection.update_one(
        {'name': genre_name},
        {'$addToSet': {'books': data['title']}}  # Using addToSet to avoid duplicates
    )

    if result.modified_count or result.matched_count:
        genre = genres_collection.find_one({'name': genre_name}, {'_id': 0})
        return jsonify({"message": "Book added to genre", "genre": genre}), 200
    return jsonify({"message": "Genre not found"}), 404

@app.route('/genres/<genre_name>', methods=['PUT'])
def update_genre(genre_name):
    """Update a genre."""
    data = request.json
    if 'name' not in data or 'description' not in data:
        return jsonify({"error": "Invalid genre data. 'name' and 'description' are required."}), 400

    # Get existing genre to preserve books
    existing_genre = genres_collection.find_one({'name': genre_name})
    if not existing_genre:
        return jsonify({"message": "Genre not found"}), 404

    updated_genre = {
        "name": data['name'],
        "description": data['description'],
        "books": existing_genre.get('books', [])
    }

    result = genres_collection.update_one(
        {'name': genre_name},
        {'$set': updated_genre}
    )

    if result.modified_count:
        return jsonify({"message": "Genre updated", "genre": updated_genre}), 200
    return jsonify({"message": "No changes made"}), 200

@app.route('/genres/<genre_name>', methods=['DELETE'])
def delete_genre(genre_name):
    """Delete a genre."""
    result = genres_collection.delete_one({'name': genre_name})
    if result.deleted_count:
        return jsonify({"message": "Genre deleted"}), 200
    return jsonify({"message": "Genre not found"}), 404

@app.route('/genres/<genre_name>/books/<book_title>', methods=['DELETE'])
def remove_book_from_genre(genre_name, book_title):
    """Remove a book from a genre."""
    result = genres_collection.update_one(
        {'name': genre_name},
        {'$pull': {'books': book_title}}
    )

    if result.modified_count:
        genre = genres_collection.find_one({'name': genre_name}, {'_id': 0})
        return jsonify({"message": "Book removed from genre", "genre": genre}), 200
    return jsonify({"message": "Genre or book not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8013)

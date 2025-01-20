from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from pymongo import MongoClient
from bson import ObjectId
import os
from graphene import ObjectType, String, Int, List, Schema, Field, Date
from flask_graphql import GraphQLView
from datetime import datetime

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
MONGO_URI = 'mongodb+srv://Lea:123leici@cluster0.iupgk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(MONGO_URI)
db = client['library']
authors_collection = db['authors']

# GraphQL Types
class Book(ObjectType):
    title = String(required=True)
    isbn = String()
    publication_date = Date()
    genre = Field(lambda: Genre)

class Genre(ObjectType):
    name = String(required=True)
    description = String()

class Author(ObjectType):
    name = String(required=True)
    birth_date = Date()
    nationality = String()
    books = List(Book)
    biography = String()

class Query(ObjectType):
    authors = List(Author)
    author = Field(Author, name=String())
    
    def resolve_authors(self, info):
        authors_data = authors_collection.find({}, {'_id': 0})
        return [Author(**author) for author in authors_data]
    
    def resolve_author(self, info, name):
        author_data = authors_collection.find_one({'name': name}, {'_id': 0})
        if author_data:
            return Author(**author_data)
        return None

# Create GraphQL schema
schema = Schema(query=Query)

# Add GraphQL view
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Enable GraphiQL interface
    )
)

# Existing REST endpoints
@app.route('/authors', methods=['GET'])
def get_all_authors():
    """Get all authors."""
    authors = list(authors_collection.find({}, {'_id': 0}))
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
    if "name" not in data:
        return jsonify({"error": "Invalid author data"}), 400
    
    # Add additional fields for GraphQL support
    author_data = {
        "name": data["name"],
        "birth_date": data.get("birth_date"),
        "nationality": data.get("nationality"),
        "biography": data.get("biography"),
        "books": data.get("books", [])
    }
    
    if authors_collection.find_one({'name': data['name']}):
        return jsonify({"error": "Author already exists"}), 409
    
    authors_collection.insert_one(author_data)
    return jsonify({"message": "Author created", "author": author_data}), 201

# Other existing REST endpoints remain the same...

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8012)
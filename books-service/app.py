from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from pymongo import MongoClient
import os
from flask_restx import Api, Resource, fields
from functools import wraps
import jwt

app = Flask(__name__)
CORS(app)

SWAGGER_URL = '/swagger'  # URL za dostop do Swagger UI
API_URL = '/static/swagger.yaml'  # Pot do datoteke swagger.yaml v mapi static

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Books Service API"
    }
)

# --- JWT Configuration ---
JWT_SECRET_KEY = os.getenv("SECRET_KEY") #Get from environment variables
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is not set.")
JWT_ALGORITHM = "HS256"

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get('jwt_token')
        if not token:
            return jsonify({"error": "Unauthorized. Redirecting to login."}), 401

        try:
            jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired. Redirecting to login."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token. Redirecting to login."}), 401
    return wrapper
# with open('/.env') as f:
#     for line in f:
#         key, value = line.strip().split('=', 1)
#         os.environ[key] = value

MONGO_URI = 'mongodb+srv://Lea:123leici@cluster0.iupgk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'



# ---------------graphql-------------
class Book(ObjectType):
    title = String(required=True)
    author = String()
    genre = String()
    reserved = Boolean()

class Query(ObjectType):
    books = List(Book)
    book = Field(Book, title=String(required=True))

    def resolve_books(self, info):
        books_data = books_collection.find({}, {'_id': 0})
        return [Book(**book) for book in books_data]

    def resolve_book(self, info, title):
        book_data = books_collection.find_one({'title': title}, {'_id': 0})
        if book_data:
            return Book(**book_data)
        return None

class Mutation(ObjectType):
    add_book = Field(
        Book,
        title=String(required=True),
        author=String(),
        genre=String(),
        reserved=Boolean(default_value=False),
    )

    update_book = Field(
        Book,
        title=String(required=True),
        author=String(),
        genre=String(),
        reserved=Boolean(),
    )

    delete_book = Field(Boolean, title=String(required=True))

    def resolve_add_book(self, info, title, author=None, genre=None, reserved=False):
        new_book = {
            "title": title,
            "author": author,
            "genre": genre,
            "reserved": reserved,
        }
        books_collection.insert_one(new_book)
        return Book(**new_book)

    def resolve_update_book(self, info, title, author=None, genre=None, reserved=None):
        update_data = {}
        if author is not None:
            update_data["author"] = author
        if genre is not None:
            update_data["genre"] = genre
        if reserved is not None:
            update_data["reserved"] = reserved

        result = books_collection.update_one({"title": title}, {"$set": update_data})
        if result.matched_count == 0:
            return None

        updated_book = books_collection.find_one({"title": title}, {'_id': 0})
        return Book(**updated_book)

    def resolve_delete_book(self, info, title):
        result = books_collection.delete_one({"title": title})
        return result.deleted_count > 0

schema = Schema(query=Query, mutation=Mutation)

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql",
        schema=schema,
        graphiql=True
    ),
)
# ---------------graphql-------------




@app.route('/')
def login():
    return jsonify({"message": "Please log in"}), 401

if not MONGO_URI:
    raise ValueError("MONGO_URI ni nastavljen")

client = MongoClient(MONGO_URI)
db = client["library"]
collection = db["books"]


@app.route('/books', methods=['GET'])
def get_books():
    books = list(collection.find({}, {"_id": 0}))  # Vrni brez `_id`
    return jsonify(books)


@app.route('/books/<title>', methods=['GET'])
def get_book(title):
    print(f"Iskanje knjige z naslovom: {title}")
    book = collection.find_one({"title": title}, {"_id": 0})
    if book is None:
        print("Knjige ni mogoče najti.")
        return jsonify({"error": "Book not found"}), 404
    print("Knjiga najdena:", book)
    return jsonify(book), 200

@app.route('/books', methods=['POST'])

def add_book():
    data = request.json
    data["reserved"] = data.get("reserved", False)  # Nastavi na False, če polje ne obstaja
    collection.insert_one(data)
    return jsonify({"message": "Book added successfully"}), 201

@app.route('/books/<string:title>', methods=['DELETE'])
def delete_book(title):
    if request.method == 'DELETE':
        result = collection.delete_one({"title": title})
        if result.deleted_count == 0:
            return jsonify({"error": "Book not found"}), 404
        return jsonify({"message": "Book deleted successfully"}), 200

@app.route('/books/<string:title>', methods=['PUT'])
def update_book(title):
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    result = collection.update_one({"title": title}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": "Book updated successfully"}), 200

@app.route('/books/<title>/availability', methods=['GET'])
def check_availability(title):
    book = collection.find_one({"title": title}, {"_id": 0})
    if not book:
        return jsonify({"error": "Book not found"}), 404

    available = not book.get("reserved", False)
    return jsonify({"available": available})

@app.route('/books/<title>/reserve', methods=['PUT'])
def update_availability(title):
    data = request.json
    reserved_status = data.get("reserved", False)

    result = collection.update_one(
        {"title": title},
        {"$set": {"reserved": reserved_status}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Book not found"}), 404

    return jsonify({"message": "Book availability updated successfully"}), 200

@app.route('/books/<title>/reserve', methods=['POST'])
def reserve_book(title):
    result = collection.update_one(
        {"title": title, "available": True},
        {"$set": {"available": False}}
    )
    if result.matched_count == 0:
        return jsonify({"error": "Book not available or already reserved"}), 400
    return jsonify({"message": "Book reserved successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)

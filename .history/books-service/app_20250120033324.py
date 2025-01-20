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
            return redirect(url_for('login'))

        try:
            jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            return redirect(url_for('login'))
    return wrapper
# with open('/.env') as f:
#     for line in f:
#         key, value = line.strip().split('=', 1)
#         os.environ[key] = value

MONGO_URI = 'mongodb+srv://Lea:123leici@cluster0.iupgk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'


@app.route('/login')
def login():
    return jsonify({"message": "Please log in"}), 401

if not MONGO_URI:
    raise ValueError("MONGO_URI ni nastavljen")

client = MongoClient(MONGO_URI)
db = client["library"]
collection = db["books"]


@app.route('/books', methods=['GET'])
@jwt_required
def get_books():
    books = list(collection.find({}, {"_id": 0}))  # Vrni brez `_id`
    return jsonify(books)


@app.route('/books/<title>', methods=['GET'])
@jwt_required
def get_book(title):
    print(f"Iskanje knjige z naslovom: {title}")
    book = collection.find_one({"title": title}, {"_id": 0})
    if book is None:
        print("Knjige ni mogoče najti.")
        return jsonify({"error": "Book not found"}), 404
    print("Knjiga najdena:", book)
    return jsonify(book), 200

@app.route('/books', methods=['POST'])
@jwt_required
def add_book():
    data = request.json
    data["reserved"] = data.get("reserved", False)  # Nastavi na False, če polje ne obstaja
    collection.insert_one(data)
    return jsonify({"message": "Book added successfully"}), 201

@app.route('/books/<string:title>', methods=['DELETE'])
@jwt_required
def delete_book(title):
    if request.method == 'DELETE':
        result = collection.delete_one({"title": title})
        if result.deleted_count == 0:
            return jsonify({"error": "Book not found"}), 404
        return jsonify({"message": "Book deleted successfully"}), 200

@app.route('/books/<string:title>', methods=['PUT'])
@jwt_required
def update_book(title):
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    result = collection.update_one({"title": title}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": "Book updated successfully"}), 200

@app.route('/books/<title>/availability', methods=['GET'])
@jwt_required
def check_availability(title):
    book = collection.find_one({"title": title}, {"_id": 0})
    if not book:
        return jsonify({"error": "Book not found"}), 404

    available = not book.get("reserved", False)
    return jsonify({"available": available})

@app.route('/books/<title>/reserve', methods=['PUT'])
@jwt_required
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
@jwt_required
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

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from flask_swagger_ui import get_swaggerui_blueprint
import os

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

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

with open('/.env') as f:
    for line in f:
        key, value = line.strip().split('=', 1)
        os.environ[key] = value

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI ni nastavljen")

client = MongoClient(MONGO_URI)
db = client["library"]
collection = db["users"]


@app.route('/users', methods=['GET'])
def get_users():
    users = list(collection.find({}, {"_id": 0}))  # Vrni brez `_id`
    return jsonify(users)


@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    if not all(key in data for key in ("username", "email")):
        return jsonify({"error": "Missing fields"}), 400
    collection.insert_one(data)
    return jsonify({"message": "User added successfully"}), 201


@app.route('/users/<string:username>', methods=['DELETE'])
def delete_user(username):
    result = collection.delete_one({"username": username})
    if result.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User deleted successfully"}), 200


@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    user = collection.find_one({"username": username}, {"_id": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


if __name__ == '__main__':
    app.run(debug=True, port=8002)

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import requests
from flask_swagger_ui import get_swaggerui_blueprint
from graphene import ObjectType, String, List, Schema, Field
import graphene
from flask_graphql import GraphQLView

app = Flask(__name__)
CORS(app)

# Swagger setup
SWAGGER_URL = '/swagger'
API_URL = '/static/recommendations.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Recommendations Service API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# MongoDB setup
MONGO_URI = 'mongodb+srv://Lea:123leici@cluster0.iupgk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set")

client = MongoClient(MONGO_URI)
db = client["library"]
collection = db["recommendations"]

# GraphQL Types
class RecommendationType(ObjectType):
    user = String()
    book_title = String()
    added_date = String()

class Query(ObjectType):
    recommendations = List(RecommendationType, user=String(required=True))
    
    def resolve_recommendations(self, info, user):
        recommendations = list(collection.find({"user": user}, {"_id": 0}))
        return [RecommendationType(user=rec["user"], book_title=rec["book_title"], added_date=rec["added_date"]) for rec in recommendations]

# GraphQL Schema
schema = Schema(query=Query)

# GraphQL route
app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql', schema=schema, graphiql=True))  # graphiql=True enables the interactive GraphiQL interface

# REST API Routes

# Endpoint: Get all recommendations (GET)
@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    user = request.args.get('user')
    query = {"user": user} if user else {}
    recommendations = list(collection.find(query, {"_id": 0}))
    return jsonify(recommendations), 200

# Endpoint: Add a recommendation (POST)
@app.route('/recommendations', methods=['POST'])
def add_recommendation():
    data = request.json
    user = data.get("user")
    book_title = data.get("book_title")

    if not user or not book_title:
        return jsonify({"error": "User and book title are required"}), 400

    recommendation = {
        "user": user,
        "book_title": book_title,
        "added_date": datetime.now().isoformat()
    }

    collection.insert_one(recommendation)
    return jsonify({"message": "Recommendation added successfully"}), 201

# Endpoint: Update recommendations for a user (PUT)
@app.route('/recommendations/<user>', methods=['PUT'])
def update_recommendations(user):
    data = request.json  # Expect a list of book titles
    if not isinstance(data, list):
        return jsonify({"error": "Invalid data format. Expected a list."}), 400

    # Remove old recommendations and add new ones
    collection.delete_many({"user": user})
    new_recommendations = [{"user": user, "book_title": title, "added_date": datetime.now().isoformat()} for title in data]
    collection.insert_many(new_recommendations)

    return jsonify({"message": "Recommendations updated successfully"}), 200

# Endpoint: Delete all recommendations for a user (DELETE)
@app.route('/recommendations/<user>', methods=['DELETE'])
def delete_recommendations(user):
    result = collection.delete_many({"user": user})
    if result.deleted_count == 0:
        return jsonify({"error": "No recommendations found for the user"}), 404

    return jsonify({"message": "Recommendations deleted successfully"}), 200

# Endpoint: Suggest a genre (GET)
@app.route('/recommendations/<user>/suggest_genre', methods=['GET'])
def suggest_genre(user):
    user_recommendations = list(collection.find({"user": user}, {"_id": 0, "book_title": 1}))

    if not user_recommendations:
        return jsonify({"message": "No recommendations found for this user"}), 404

    # Dummy logic to suggest a genre (replace with real logic)
    recommended_titles = [rec["book_title"] for rec in user_recommendations]
    if any("Sci-Fi" in title for title in recommended_titles):
        suggested_genre = "Sci-Fi"
    elif any("Mystery" in title for title in recommended_titles):
        suggested_genre = "Mystery"
    else:
        suggested_genre = "General Fiction"

    try:
        response = requests.get(f"http://localhost:8013/genres/{suggested_genre}")
        response.raise_for_status()
        genre_details = response.json()
        return jsonify({"suggested_genre": genre_details}), 200
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Genres Service: {e}")
        return jsonify({"error": "Could not retrieve genre details"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8011)

from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from pymongo import MongoClient
import requests
import os
from flask_swagger_ui import get_swaggerui_blueprint
from bson import ObjectId
from graphene import ObjectType, String, Int, List, Field, Date, Schema
from graphene import Date
from datetime import datetime
from flask_graphql import GraphQLView

# Initialize Flask and CORS
app = Flask(__name__)
CORS(app)

# Swagger setup
SWAGGER_URL = '/swagger'  
API_URL = '/static/swagger.yaml'  
SECRET_KEY = os.getenv("SECRET_KEY")
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Books Service API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# MongoDB setup
MONGO_URI = 'mongodb+srv://Lea:123leici@cluster0.iupgk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(MONGO_URI)
db = client["library"]
collection = db["feedback"]

# GraphQL Types
class FeedbackType(ObjectType):
    id = String()
    username = String()
    message = String()
    rating = Int()
    status = String()
    created_at = Date()

class UserType(ObjectType):
    username = String()
    email = String()
    created_at = Date()

class Query(ObjectType):
    all_feedback = List(FeedbackType)
    feedback_by_username = Field(FeedbackType, username=String(required=True))
    all_users = List(UserType)

    def resolve_all_feedback(self, info):
        feedback_list = list(collection.find({}, {"_id": 0}))
        return [FeedbackType(
            id=str(feedback["_id"]),
            username=feedback["username"],
            message=feedback["message"],
            rating=feedback["rating"],
            status=feedback["status"],
            created_at=datetime.strptime(feedback.get("created_at", ""), "%Y-%m-%dT%H:%M:%S") if "created_at" in feedback else datetime.now()
        ) for feedback in feedback_list]

    def resolve_feedback_by_username(self, info, username):
        feedback = collection.find_one({"username": username})
        if feedback:
            return FeedbackType(
                id=str(feedback["_id"]),
                username=feedback["username"],
                message=feedback["message"],
                rating=feedback["rating"],
                status=feedback["status"],
                created_at=datetime.strptime(feedback.get("created_at", ""), "%Y-%m-%dT%H:%M:%S") if "created_at" in feedback else datetime.now()
            )
        return None

    def resolve_all_users(self, info):
        users = [{"username": "lea", "email": "lea@example.com", "created_at": datetime.now()}]
        return [UserType(username=user["username"], email=user["email"], created_at=user["created_at"]) for user in users]

# GraphQL Schema
schema = Schema(query=Query)

# REST API routes for feedback management (same as your current code)
@app.route('/feedback', methods=['GET'])
def get_feedbacks():
    feedback_list = list(collection.find({}, {"_id": 0}))
    return jsonify(feedback_list), 200

@app.route('/feedback', methods=['POST'])
def add_feedback():
    data = request.json
    username = data.get('username')
    message = data.get('message')
    rating = data.get('rating')

    if not username or not message or not rating:
        return jsonify({"error": "Manjkajoči podatki v zahtevi."}), 400

    user_response = requests.get(f"http://localhost:8002/users/{username}")
    if user_response.status_code == 404:
        return jsonify({"error": "Uporabnik ni bil najden."}), 404

    feedback = {
        "username": username,
        "message": message,
        "rating": rating,
        "status": "pending"
    }
    result = collection.insert_one(feedback)
    feedback["_id"] = str(result.inserted_id)
    return jsonify(feedback), 201

@app.route('/feedback/<username>/approve', methods=['POST'])
def approve_feedback(username):
    user_feedbacks = list(collection.find({"username": username}))
    if not user_feedbacks:
        return jsonify({"error": "No feedback found for this user"}), 404
    for feedback in user_feedbacks:
        collection.update_one(
            {"_id": feedback["_id"]},
            {"$set": {"status": "approved"}}
        )
    return jsonify({"message": "Feedback approved successfully", "feedbacks": user_feedbacks}), 200

@app.route('/feedback/<username>/reject', methods=['POST'])
def reject_feedback(username):
    user_feedbacks = list(collection.find({"username": username}))
    if not user_feedbacks:
        return jsonify({"error": "No feedback found for this user"}), 404
    for feedback in user_feedbacks:
        collection.update_one(
            {"_id": feedback["_id"]},
            {"$set": {"status": "rejected"}}
        )
    return jsonify({"message": "Feedback rejected successfully", "feedbacks": user_feedbacks}), 200

@app.route('/feedback/<username>', methods=['DELETE'])
def delete_feedback(username):
    result = collection.delete_one({"username": username})
    if result.deleted_count == 0:
        return jsonify({"error": "Feedback not found"}), 404
    return jsonify({"message": "Feedback deleted successfully"}), 200

# Adding GraphQL route
app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql', schema=schema, graphiql=True))  # graphiql=True enables GraphiQL interface for testing queries

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8003)

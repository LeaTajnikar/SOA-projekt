from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests
import os
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)

# Swagger setup
SWAGGER_URL = '/swagger'  # URL for accessing Swagger UI
API_URL = '/static/swagger.yaml'  # Path to swagger.yaml file in the static directory
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Feedback Service API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://Lea:123leici@cluster0.iupgk.mongodb.net/library?retryWrites=true&w=majority')
if not MONGO_URI:
    raise ValueError("MONGO_URI is not set")

client = MongoClient(MONGO_URI)
db = client["library"]
feedback_collection = db["feedback"]

# External service URLs
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:8002/users/")
BOOKS_SERVICE_URL = os.getenv("BOOKS_SERVICE_URL", "http://localhost:8001/books/")

# Routes
@app.route('/feedback', methods=['GET'])
def get_feedbacks():
    """Retrieve all feedback."""
    feedback_list = list(feedback_collection.find({}, {"_id": 0}))
    return jsonify(feedback_list), 200

@app.route('/feedback', methods=['POST'])
def add_feedback():
    """Add new feedback."""
    data = request.json
    username = data.get('username')
    message = data.get('message')
    rating = data.get('rating')

    if not username or not message or not rating:
        return jsonify({"error": "Missing required fields: 'username', 'message', 'rating'"}), 400

    # Verify user existence
    user_response = requests.get(f"{USERS_SERVICE_URL}{username}")
    if user_response.status_code == 404:
        return jsonify({"error": "User not found"}), 404

    # Save feedback to database
    feedback = {
        "username": username,
        "message": message,
        "rating": rating,
        "status": "pending"
    }
    result = feedback_collection.insert_one(feedback)
    feedback["_id"] = str(result.inserted_id)
    return jsonify(feedback), 201

@app.route('/feedback/<username>/approve', methods=['POST'])
def approve_feedback(username):
    """Approve feedback for a user."""
    user_feedbacks = list(feedback_collection.find({"username": username}))
    if not user_feedbacks:
        return jsonify({"error": "No feedback found for this user"}), 404

    for feedback in user_feedbacks:
        feedback_collection.update_one(
            {"_id": feedback["_id"]},
            {"$set": {"status": "approved"}}
        )
    return jsonify({"message": "Feedback approved successfully", "feedbacks": user_feedbacks}), 200

@app.route('/feedback/<username>/reject', methods=['POST'])
def reject_feedback(username):
    """Reject feedback for a user."""
    user_feedbacks = list(feedback_collection.find({"username": username}))
    if not user_feedbacks:
        return jsonify({"error": "No feedback found for this user"}), 404

    for feedback in user_feedbacks:
        feedback_collection.update_one(
            {"_id": feedback["_id"]},
            {"$set": {"status": "rejected"}}
        )
    return jsonify({"message": "Feedback rejected successfully", "feedbacks": user_feedbacks}), 200

@app.route('/feedback/<username>', methods=['DELETE'])
def delete_feedback(username):
    """Delete feedback for a user."""
    result = feedback_collection.delete_one({"username": username})
    if result.deleted_count == 0:
        return jsonify({"error": "Feedback not found"}), 404
    return jsonify({"message": "Feedback deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8012)

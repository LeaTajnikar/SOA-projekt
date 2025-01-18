from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests
import os


app = Flask(__name__)
CORS(app)


with open('../.env') as f:
    for line in f:
        key, value = line.strip().split('=', 1)
        os.environ[key] = value

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI ni nastavljen")

client = MongoClient(MONGO_URI)
db = client["library"]
collection = db["feedback"]


@app.route('/feedback', methods=['GET'])
def get_feedback():
    feedback_list = list(collection.find({}, {"_id": 0}))  # Vrni brez `_id`
    return jsonify(feedback_list)


# Povezava na Users Service za preverjanje obstoja uporabnika
USERS_SERVICE_URL = "http://localhost:8001/users/"

@app.route('/feedbacks', methods=['POST'])
def add_feedback():
    data = request.json
    username = data.get('username')
    feedback_content = data.get('feedback')

    # Preveri, ali uporabnik obstaja v Users Service
    user_response = requests.get(f"{USERS_SERVICE_URL}{username}")
    if user_response.status_code == 404:
        return jsonify({"error": "User not found"}), 404

    # Shrani feedback v MongoDB
    feedback = {
        "username": username,
        "feedback": feedback_content,
        "status": "pending"
    }
    collection.insert_one(feedback)

    return jsonify({"message": "Feedback submitted successfully", "feedback": feedback}), 201

@app.route('/feedbacks/<username>', methods=['GET'])
def get_feedbacks(username):
    # Poišči vse feedbacke za določenega uporabnika v MongoDB
    user_feedbacks = list(collection.find({"username": username}))

    if not user_feedbacks:
        return jsonify({"error": "No feedback found for this user"}), 404

    return jsonify({"feedbacks": user_feedbacks}), 200

@app.route('/feedbacks/<username>/approve', methods=['POST'])
def approve_feedback(username):
    # Poišči feedback za uporabnika v MongoDB
    user_feedbacks = list(collection.find({"username": username}))

    if not user_feedbacks:
        return jsonify({"error": "No feedback found for this user"}), 404

    # Posodobi stanje feedbacka na 'approved'
    for feedback in user_feedbacks:
        collection.update_one(
            {"_id": feedback["_id"]},
            {"$set": {"status": "approved"}}
        )

    return jsonify({"message": "Feedback approved successfully", "feedbacks": user_feedbacks}), 200

@app.route('/feedbacks/<username>/reject', methods=['POST'])
def reject_feedback(username):
    # Poišči feedback za uporabnika v MongoDB
    user_feedbacks = list(collection.find({"username": username}))

    if not user_feedbacks:
        return jsonify({"error": "No feedback found for this user"}), 404

    # Posodobi stanje feedbacka na 'rejected'
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


if __name__ == '__main__':
    app.run(debug=True, port=8003)

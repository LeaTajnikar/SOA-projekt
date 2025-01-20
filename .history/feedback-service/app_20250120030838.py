from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests
import os
from flask_swagger_ui import get_swaggerui_blueprint
from bson import ObjectId

app = Flask(__name__)
CORS(app)

SWAGGER_URL = '/swagger'  # URL za dostop do Swagger UI
API_URL = '/static/swagger.yaml'  # Pot do datoteke swagger.yaml v mapi static
SECRET_KEY = os.getenv("SECRET_KEY",'secret')
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Books Service API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)



MONGO_URI = 'mongodb+srv://Lea:123leici@cluster0.iupgk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

if not MONGO_URI:
    raise ValueError("MONGO_URI ni nastavljen")

client = MongoClient(MONGO_URI)
db = client["library"]
collection = db["feedback"]


@app.route('/feedback', methods=['GET'])
def get_feedbacks():
    feedback_list = list(collection.find({}, {"_id": 0}))  # Vrne vse feedbacke brez `_id`
    return jsonify(feedback_list), 200


# Povezava na Users Service za preverjanje obstoja uporabnika
USERS_SERVICE_URL = "http://localhost:8002/users/"
BOOKS_SERVICE_URL = "http://localhost:8001/books/"


@app.route('/feedback', methods=['POST'])
def add_feedback():
    data = request.json
    username = data.get('username')
    message = data.get('message')
    rating = data.get('rating')

    if not username or not message or not rating:
        return jsonify({"error": "Manjkajoči podatki v zahtevi."}), 400

    print(f"Prejeta zahteva za dodajanje feedbacka: {data}")

    # Preveri obstoj uporabnika
    user_response = requests.get(f"{USERS_SERVICE_URL}{username}")
    if user_response.status_code == 404:
        print(f"Uporabnik ni bil najden.")
        return jsonify({"error": "Uporabnik ni bil najden."}), 404

    print(f"Preverjanje uporabnika ({username}): {user_response.status_code}")


    # Shrani feedback v bazo
    feedback = {
        "username": username,
        "message": message,
        "rating": rating,
        "status": "pending"
    }
    result = collection.insert_one(feedback)

    # Dodaj `_id` kot string v odgovor
    feedback["_id"] = str(result.inserted_id)
    print(f"Feedback uspešno dodan: {feedback}")

    return jsonify(feedback), 201

@app.route('/feedback/<username>/approve', methods=['POST'])
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

@app.route('/feedback/<username>/reject', methods=['POST'])
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
    app.run(debug=True, host='0.0.0.0', port=8003)

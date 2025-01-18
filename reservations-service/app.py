from bson import ObjectId
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timedelta
import requests
import os

# Ustvari aplikacijo Flask
app = Flask(__name__)
CORS(app)

# Povezava z MongoDB
with open('../.env') as f:
    for line in f:
        key, value = line.strip().split('=', 1)
        os.environ[key] = value

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI ni nastavljen")

client = MongoClient(MONGO_URI)
db = client["library"]
collection = db["reservations"]
reservations_collection = db["reservations"]

# Konfiguracija omejitev
MAX_RESERVATIONS = 3
RESERVATION_DURATION_DAYS = 7


# Endpoint za pridobivanje vseh rezervacij (GET)
@app.route('/reservations', methods=['GET'])
def get_reservations():
    user = request.args.get('user')
    book_title = request.args.get('book_title')

    query = {}
    if user:
        query["username"] = user
    if book_title:
        query["book_title"] = book_title

    reservations = list(reservations_collection.find(query, {"_id": 0}))  # Vrni brez `_id`
    return jsonify(reservations)

@app.route('/reservations/active', methods=['GET'])
def get_active_reservations():
    now = datetime.utcnow()
    active_reservations = list(reservations_collection.find({"expiration_date": {"$gte": now.isoformat()}}, {"_id": 0}))
    return jsonify(active_reservations), 200

@app.route('/reservations/<username>/<book_title>', methods=['DELETE'])
def delete_reservation(username, book_title):
    # Izbriši rezervacijo iz baze
    result = reservations_collection.delete_one({"username": username, "book_title": book_title})

    if result.deleted_count == 0:
        return jsonify({"error": "Reservation not found"}), 404

    # Posodobi status knjige v Books Service
    book_service_url = f"http://localhost:8001/books/{book_title}"
    update_response = requests.put(book_service_url, json={"reserved": False})
    if update_response.status_code != 200:
        return jsonify({"error": "Failed to update book status"}), 500

    return jsonify({"message": "Reservation deleted and book status updated"}), 200



# Endpoint za podaljšanje rezervacije (PUT)
@app.route('/reservations/<username>/<book_title>/extend', methods=['PUT'])
def extend_reservation(username, book_title):
    # Preveri, ali rezervacija obstaja
    reservation = reservations_collection.find_one({"username": username, "book_title": book_title})
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    current_expiration_date = datetime.strptime(reservation["expiration_date"][:10], "%Y-%m-%d")
    new_expiration_date = current_expiration_date + timedelta(days=7)
    # Podaljšaj datum poteka rezervacije za 7 dni
    #new_expiration_date = datetime.strptime(reservation["expiration_date"], "%Y-%m-%d") + timedelta(days=7)
    reservations_collection.update_one(
        {"username": username, "book_title": book_title},
        {"$set": {"expiration_date": new_expiration_date.strftime("%Y-%m-%d")}}
    )
    return jsonify({"message": "Reservation extended successfully", "new_expiration_date": new_expiration_date.strftime("%Y-%m-%d")}), 200


# Endpoint za dodajanje nove rezervacije
@app.route('/reservations', methods=['POST'])
def add_reservation():
    data = request.json
    username = data["username"]
    book_title = data["book_title"]

    # Preveri število obstoječih rezervacij uporabnika
    user_reservations = reservations_collection.count_documents({"username": username})
    if user_reservations >= MAX_RESERVATIONS:
        return jsonify({"error": "User has reached the maximum number of reservations"}), 400

    # Preveri stanje knjige v Books Service
    book_response = requests.get(f"http://localhost:8001/books/{book_title}")
    if book_response.status_code == 404 or book_response.json().get("reserved", False) == True:
        return jsonify({"error": "Book not available"}), 400

    # Dodaj expiration_date k rezervaciji
    reservation_date = datetime.now().strftime("%Y-%m-%d")
    expiration_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    reservation = {
        "username": username,
        "book_title": book_title,
        "reservation_date": reservation_date,
        "expiration_date": expiration_date,
    }

    # Dodaj rezervacijo
    reservations_collection.insert_one(reservation)

    # Posodobi stanje knjige na "reserved: True"
    requests.put(f"http://localhost:8002/books/{book_title}", json={"reserved": True})

    return jsonify({"message": "Reservation added successfully"}), 201


# Zaženi strežnik
if __name__ == '__main__':
    app.run(debug=True, port=8005)
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests
from flask_swagger_ui import get_swaggerui_blueprint
import os

# Ustvari aplikacijo Flask
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

# Povezava z MongoDB
with open('/.env') as f:
    for line in f:
        key, value = line.strip().split('=', 1)
        os.environ[key] = value

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI ni nastavljen")

client = MongoClient(MONGO_URI)
db = client["library"]
collection = db["notifications"]


RESERVATIONS_SERVICE_URL = "http://localhost:8005/reservations/"

# Endpoint za pošiljanje obvestila uporabniku
@app.route('/notifications/<username>', methods=['POST'])
def send_notification(username):
    # URL za dostop do uporabniškega servisa
    users_service_url = f"http://localhost:8001/users/{username}"

    try:
        # Pošlji GET zahtevo za pridobitev uporabniških podatkov
        user_response = requests.get(users_service_url)

        if user_response.status_code != 200:
            return jsonify({"error": "User not found"}), 404

        user_data = user_response.json()
        email = user_data.get('email')

        if not email:
            return jsonify({"error": "Email not available for the user"}), 400

        # Pridobi podatke obvestila iz telesa zahteve
        notification_data = request.json
        message = notification_data.get("message")

        if not message:
            return jsonify({"error": "Notification message is required"}), 400

        # Simulacija pošiljanja obvestila (trenutno samo print)
        print(f"Sending notification to {email}: {message}")

        # Simuliraj uspešno pošiljanje
        return jsonify({"message": "Notification sent successfully"}), 200

    except requests.exceptions.RequestException as e:
        # Če pride do napake pri komunikaciji z Users Service
        return jsonify({"error": "Failed to connect to Users Service", "details": str(e)}), 500

#@app.route('/notify', methods=['POST'])
#def send_notification():
#    data = request.json
#    username = data.get("username")
#    book_title = data.get("book_title")
#    message = f"Hello {username}, your reservation for '{book_title}' has been processed successfully."

    # Pošiljanje obvestila
#    print(f"Notification sent: {message}")
#    return jsonify({"message": "Notification sent"}), 200

# Endpoint za pridobivanje vseh notifikacij (GET)
@app.route('/notifications', methods=['GET'])
def get_notifications():
    notifications = list(collection.find({}, {"_id": 0}))  # Vrni brez `_id`
    return jsonify(notifications)

# Endpoint za dodajanje nove notifikacije (POST)
@app.route('/notifications', methods=['POST'])
def add_notification():
    data = request.json
    # Preveri, ali so vsa potrebna polja prisotna
    if not all(key in data for key in ("title", "message", "user")):
        return jsonify({"error": "Missing fields"}), 400
    collection.insert_one(data)
    return jsonify({"message": "Notification added successfully"}), 201

# Endpoint za brisanje notifikacije glede na naslov (DELETE)
@app.route('/notifications/<title>', methods=['DELETE'])
def delete_notification(title):
    result = collection.delete_one({"title": title})
    if result.deleted_count == 0:
        return jsonify({"error": "Notification not found"}), 404
    return jsonify({"message": "Notification deleted successfully"}), 200




def create_notification(username, message):
    notification = {
        "title": "Bilo je zbrisano",
        "message": message,
        "user": username
    }
    collection.insert_one(notification)
    print(f"Notification created: {notification}")


# Endpoint za obdelavo obvestila, ko se ustvari rezervacija
@app.route('/notifications/reservation-created', methods=['POST'])
def reservation_created_notification():
    data = request.json
    username = data.get("user")
    book_title = data.get("title")
    message = data.get("message")

    if not all([username, book_title, message]):
        return jsonify({"error": "Missing username, book_title, or message"}), 400

    # Logika za obdelavo obvestila
    print(f"Notification: {message}")
    collection.insert_one(data)
    return jsonify({"message": "Notification processed successfully"}), 200

# Endpoint za obdelavo obvestila, ko se izbriše rezervacija
@app.route('/notifications/reservation-deleted', methods=['POST'])
def reservation_deleted_notification():
    data = request.json
    username = data.get("user")
    book_title = data.get("title")
    message = data.get("message")

    if not all([username, book_title, message]):
        return jsonify({"error": "Missing username, book_title, or message"}), 400

    # Logika za obdelavo obvestila
    print(f"Notification: {message}")
    collection.insert_one(data)
    return jsonify({"message": "Notification processed successfully"}), 200


# Zaženi strežnik
if __name__ == '__main__':
    app.run(debug=True, port=8004)

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
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



MONGO_URI = 'mongodb+srv://Lea:123leici@cluster0.iupgk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

if not MONGO_URI:
    raise ValueError("MONGO_URI ni nastavljen")

client = MongoClient(MONGO_URI)
db = client["library"]
stats_collection = db["stats"]


RESERVATIONS_SERVICE_URL = "http://localhost:8005/reservations"

@app.route('/stats', methods=['GET'])
def get_all_stats():
    """Pridobi vse zapise iz statistike."""
    try:
        stats = list(stats_collection.find({}, {"_id": 0}))  # Vrni brez `_id`
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/stats/<stat_id>', methods=['GET'])
def get_stat(stat_id):
    """Pridobi določen zapis iz statistike."""
    try:
        stat = stats_collection.find_one({"_id": ObjectId(stat_id)})
        if not stat:
            return jsonify({"error": "Statistic record not found"}), 404
        stat["_id"] = str(stat["_id"])  # Pretvori ObjectId v string
        return jsonify(stat), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/stats', methods=['POST'])
def create_stat():
    """Ustvari nov zapis za statistiko."""
    data = request.json
    if not data or not all(key in data for key in ("type", "value")):
        return jsonify({"error": "Missing required fields: 'type' and 'value'"}), 400

    try:
        new_stat = {
            "type": data["type"],  # Na primer: "reservations"
            "value": data["value"],  # Na primer: 100
            "description": data.get("description", "")
        }
        result = stats_collection.insert_one(new_stat)
        new_stat["_id"] = str(result.inserted_id)  # Pretvori ObjectId v string
        return jsonify(new_stat), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/stats/<stat_id>', methods=['PUT'])
def update_stat(stat_id):
    """Posodobi obstoječi zapis v statistiki."""
    data = request.json
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    try:
        result = stats_collection.update_one(
            {"_id": ObjectId(stat_id)},
            {"$set": data}
        )
        if result.matched_count == 0:
            return jsonify({"error": "Statistic record not found"}), 404

        return jsonify({"message": "Statistic record updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/stats/<stat_id>', methods=['DELETE'])
def delete_stat(stat_id):
    """Izbriši zapis iz statistike."""
    try:
        result = stats_collection.delete_one({"_id": ObjectId(stat_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Statistic record not found"}), 404

        return jsonify({"message": "Statistic record deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['PUT'])
def izracunaj_statistiko():
    try:
        # Pridobi rezervacije iz mikrostoritve za rezervacije
        response = requests.get(RESERVATIONS_SERVICE_URL)
        if response.status_code != 200:
            return jsonify({"error": "Napaka pri pridobivanju rezervacij"}), response.status_code

        rezervacije = response.json()
        total_reservations = len(rezervacije)

        # Posodobi statistiko v bazi
        stats_data = {
            "type": "reservations",
            "value": total_reservations,
            "description": "Total reservations"
        }
        stats_collection.update_one({"type": "reservations"}, {"$set": stats_data}, upsert=True)

        return jsonify({"message": "Statistika posodobljena", "stats": stats_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8006)

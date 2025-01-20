from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timedelta
import requests
from flask_swagger_ui import get_swaggerui_blueprint
import graphene
from flask_graphql import GraphQLView

app = Flask(__name__)
CORS(app)

# Swagger setup
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yaml'

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
reservations_collection = db["reservations"]

# GraphQL setup
class ReservationType(graphene.ObjectType):
    username = graphene.String()
    book_title = graphene.String()
    reservation_date = graphene.String()
    expiration_date = graphene.String()

class Query(graphene.ObjectType):
    # GraphQL query to get reservations by username and book title
    reservations = graphene.List(ReservationType, username=graphene.String(), book_title=graphene.String())

    def resolve_reservations(self, info, username=None, book_title=None):
        query = {}
        if username:
            query["username"] = username
        if book_title:
            query["book_title"] = book_title
        reservations = list(reservations_collection.find(query, {"_id": 0}))
        return [ReservationType(**rec) for rec in reservations]

class Mutation(graphene.ObjectType):
    # Mutation to add a reservation
    add_reservation = graphene.Field(ReservationType, username=graphene.String(), book_title=graphene.String())

    def resolve_add_reservation(self, info, username, book_title):
        # Check if user has already reached the maximum number of reservations
        MAX_RESERVATIONS = 3
        user_reservations = reservations_collection.count_documents({"username": username})
        if user_reservations >= MAX_RESERVATIONS:
            raise Exception("User has reached the maximum number of reservations")

        # Check if the book is available
        book_response = requests.get(f"http://localhost:8001/books/{book_title}")
        if book_response.status_code == 404 or book_response.json().get("reserved", False):
            raise Exception("Book not available")

        # Create reservation
        reservation_date = datetime.now().strftime("%Y-%m-%d")
        expiration_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        reservation = {
            "username": username,
            "book_title": book_title,
            "reservation_date": reservation_date,
            "expiration_date": expiration_date,
        }

        reservations_collection.insert_one(reservation)
        requests.put(f"http://localhost:8001/books/{book_title}", json={"reserved": True})

        return ReservationType(username=username, book_title=book_title, reservation_date=reservation_date, expiration_date=expiration_date)

# GraphQL Schema
schema = graphene.Schema(query=Query, mutation=Mutation)

# GraphQL endpoint
app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql', schema=schema, graphiql=True))  # graphiql=True enables the interactive GraphiQL interface

# REST API routes (same as before)
@app.route('/reservations', methods=['GET'])
def get_reservations():
    user = request.args.get('user')
    book_title = request.args.get('book_title')

    query = {}
    if user:
        query["username"] = user
    if book_title:
        query["book_title"] = book_title

    reservations = list(reservations_collection.find(query, {"_id": 0}))
    return jsonify(reservations)

@app.route('/reservations/active', methods=['GET'])
def get_active_reservations():
    now = datetime.utcnow()
    active_reservations = list(reservations_collection.find({"expiration_date": {"$gte": now.isoformat()}}, {"_id": 0}))
    return jsonify(active_reservations), 200

@app.route('/reservations/<username>/<book_title>', methods=['DELETE'])
def delete_reservation(username, book_title):
    result = reservations_collection.delete_one({"username": username, "book_title": book_title})
    if result.deleted_count == 0:
        return jsonify({"error": "Reservation not found"}), 404

    book_service_url = f"http://localhost:8001/books/{book_title}"
    update_response = requests.put(book_service_url, json={"reserved": False})
    if update_response.status_code != 200:
        return jsonify({"error": "Failed to update book status"}), 500

    return jsonify({"message": "Reservation deleted and book status updated"}), 200

@app.route('/reservations/<username>/<book_title>/extend', methods=['PUT'])
def extend_reservation(username, book_title):
    reservation = reservations_collection.find_one({"username": username, "book_title": book_title})
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    current_expiration_date = datetime.strptime(reservation["expiration_date"][:10], "%Y-%m-%d")
    new_expiration_date = current_expiration_date + timedelta(days=7)

    reservations_collection.update_one(
        {"username": username, "book_title": book_title},
        {"$set": {"expiration_date": new_expiration_date.strftime("%Y-%m-%d")}}
    )
    return jsonify({"message": "Reservation extended successfully", "new_expiration_date": new_expiration_date.strftime("%Y-%m-%d")}), 200

@app.route('/reservations', methods=['POST'])
def add_reservation():
    data = request.json
    username = data["username"]
    book_title = data["book_title"]

    user_reservations = reservations_collection.count_documents({"username": username})
    if user_reservations >= MAX_RESERVATIONS:
        return jsonify({"error": "User has reached the maximum number of reservations"}), 400

    book_response = requests.get(f"http://localhost:8001/books/{book_title}")
    if book_response.status_code == 404 or book_response.json().get("reserved", False) == True:
        return jsonify({"error": "Book not available"}), 400

    reservation_date = datetime.now().strftime("%Y-%m-%d")
    expiration_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    reservation = {
        "username": username,
        "book_title": book_title,
        "reservation_date": reservation_date,
        "expiration_date": expiration_date,
    }

    reservations_collection.insert_one(reservation)

    requests.put(f"http://localhost:8001/books/{book_title}", json={"reserved": True})

    return jsonify({"message": "Reservation added successfully"}), 201


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8005)

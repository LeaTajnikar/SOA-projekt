from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from graphene import ObjectType, String, Boolean, Field, Mutation, Schema
import graphene
from flask_graphql import GraphQLView
import requests

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB setup
MONGO_URI = 'mongodb+srv://Lea:123leici@cluster0.iupgk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set")

client = MongoClient(MONGO_URI)
db = client["library"]
collection = db["notifications"]

# GraphQL Types
class NotificationType(ObjectType):
    title = String()
    message = String()
    user = String()

class Query(ObjectType):
    notifications = graphene.List(NotificationType)

    def resolve_notifications(self, info):
        # Fetch all notifications
        notifications = list(collection.find({}, {"_id": 0}))  # Without _id field
        return [NotificationType(**notification) for notification in notifications]

class CreateNotification(Mutation):
    class Arguments:
        user = String(required=True)
        message = String(required=True)
        title = String(required=True)

    success = Boolean()
    notification = Field(NotificationType)

    def mutate(self, info, user, message, title):
        notification_data = {
            "user": user,
            "message": message,
            "title": title
        }
        collection.insert_one(notification_data)
        notification = NotificationType(**notification_data)
        return CreateNotification(success=True, notification=notification)

class Mutation(ObjectType):
    create_notification = CreateNotification.Field()

# Create GraphQL schema
schema = Schema(query=Query, mutation=Mutation)

# GraphQL Route
app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql', schema=schema, graphiql=True))  # graphiql=True enables the GraphiQL interface

# REST API endpoints - remove or modify existing ones if not needed
@app.route('/notifications', methods=['GET'])
def get_notifications():
    notifications = list(collection.find({}, {"_id": 0}))  # Return without `_id`
    return jsonify(notifications)

@app.route('/notifications', methods=['POST'])
def add_notification():
    data = request.json
    if not all(key in data for key in ("title", "message", "user")):
        return jsonify({"error": "Missing fields"}), 400
    collection.insert_one(data)
    return jsonify({"message": "Notification added successfully"}), 201

@app.route('/notifications/<title>', methods=['DELETE'])
def delete_notification(title):
    result = collection.delete_one({"title": title})
    if result.deleted_count == 0:
        return jsonify({"error": "Notification not found"}), 404
    return jsonify({"message": "Notification deleted successfully"}), 200

# Flask setup to run the server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8004)

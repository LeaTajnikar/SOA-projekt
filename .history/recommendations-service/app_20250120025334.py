# recommendations-service.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)

# Swagger setup (same as your example)
SWAGGER_URL = '/swagger'
API_URL = '/static/recommendations.yaml' # Create this file
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={'app_name': "Recommendations Service API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

recommendations = {}  # In-memory storage for simplicity



@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Gets all recommendations or recommendations for a specific user."""
    user = request.args.get('user')
    if user:
        return jsonify(recommendations.get(user, []))
    return jsonify(recommendations)


@app.route('/recommendations/<user>', methods=['GET'])
def get_user_recommendations(user):
    """Gets recommendations for a specific user."""
    return jsonify(recommendations.get(user, []))

@app.route('/recommendations/<user>/suggest_genre', methods=['GET'])
def suggest_genre(user):
    """Suggests a genre based on user's recommendations (Connects to Genres Service)."""
    user_recs = recommendations.get(user, [])
    if not user_recs:
        return jsonify({"message": "No recommendations found for this user"}), 404

    # Logic to determine a suggested genre (replace with your actual logic)
    # This is a simplified example - you might use ML or more complex analysis
    if any("Sci-Fi" in rec for rec in user_recs):  # Example: Suggest Sci-Fi if present
        suggested_genre = "Sci-Fi"
    elif any("Mystery" in rec for rec in user_recs):
        suggested_genre = "Mystery"
    else:
        suggested_genre = "General Fiction"  # Default

    try:
        # Get genre details from Genres Service
        response = requests.get(f"http://localhost:8013/genres/{suggested_genre}")
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        genre_details = response.json()
        return jsonify({"suggested_genre": genre_details}), 200

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Genres Service: {e}")
        return jsonify({"error": "Could not retrieve genre details"}), 500  # Internal Server Erro



@app.route('/recommendations/<user>', methods=['POST'])
def add_recommendation(user):
    """Adds a recommendation for a user."""
    data = request.json
    if not data or 'book_title' not in data:
        return jsonify({"error": "Invalid data format"}), 400
    if user not in recommendations:
        recommendations[user] = []
    recommendations[user].append(data['book_title'])
    return jsonify({"message": "Recommendation added"}), 201

@app.route('/recommendations/<user>', methods=['PUT'])
def update_recommendations(user):
    """Updates recommendations for a user."""
    data = request.json  # Expect a list of book titles
    if not isinstance(data, list):
        return jsonify({"error": "Invalid data format. Expected a list."}), 400
    recommendations[user] = data
    return jsonify({"message": "Recommendations updated"}), 200



@app.route('/recommendations/<user>', methods=['DELETE'])
def delete_recommendations(user):
    """Deletes recommendations for a user."""
    if user in recommendations:
        del recommendations[user]
        return jsonify({"message": "Recommendations deleted"}), 200
    return jsonify({"message": "User not found"}), 404

@app.route('/recommendations/<user>/<book_title>', methods=['DELETE'])
def delete_single_recommendation(user, book_title):
    """Deletes a specific recommendation for a user."""

    if user in recommendations:
        if book_title in recommendations[user]:
            recommendations[user].remove(book_title)
            return jsonify({"message": "Recommendation deleted successfully"}), 200

        return jsonify({"message": "Recommendation not found for this user"}), 404
    return jsonify({"message": "User not found"}), 404





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8006)  # Choose a different port
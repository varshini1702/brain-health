from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from bson import ObjectId
from flask_cors import CORS
import datetime
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests
# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/brain_health_db"
mongo = PyMongo(app)
# Helper function to convert ObjectId to string
def convert_objectid(data):
    if isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data
# Serve the HTML frontend page
@app.route('/')
def home():
    return render_template('index.html')
# Sleep and Brain Health Correlation Analysis Endpoint
@app.route('/brain-health/sleep-analysis', methods=['POST'])
def sleep_analysis():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        sleep_patterns = data.get('sleep_patterns')
        cognitive_test_scores = data.get('cognitive_test_scores')
        brain_health_score = data.get('brain_health_score')
        if not all([user_id, sleep_patterns, cognitive_test_scores, brain_health_score]):
            return jsonify({"error": "Missing required fields"}), 400
        # Check if sleep quality and duration are within typical ranges
        duration = sleep_patterns.get("duration", 0)
        quality = sleep_patterns.get("quality", 0)
        # Basic Analysis Logic
        analysis = ""
        if duration < 6:
            analysis = "Your sleep duration is below average. Consider increasing sleep time for better health."
        elif duration >= 6 and quality >= 7:
            analysis = "You have a good level of sleep quality and duration. Keep it up!"
        elif duration >= 6 and quality < 7:
            analysis = "Sleep duration is good, but sleep quality could be improved."
        else:
            analysis = "Sleep analysis data indicates average health; consider better sleep practices."
        sleep_analysis_data = {
            "user_id": user_id,
            "sleep_patterns": sleep_patterns,
            "cognitive_test_scores": cognitive_test_scores,
            "brain_health_score": brain_health_score,
            "timestamp": datetime.datetime.utcnow()
        }
        result = mongo.db.sleep_analysis.insert_one(sleep_analysis_data)
        response_data = {
            "message": "Sleep analysis data submitted successfully",
            "id": str(result.inserted_id),
            "analysis_data": convert_objectid(sleep_analysis_data),
            "analysis": analysis  # Include the sleep analysis in the response
        }
        return jsonify(response_data), 201
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)

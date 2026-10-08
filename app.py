"""
Flask Web Application for the College Examination FAQ Chatbot.
Provides web interface and REST API endpoint /api/chat.
"""

import os
from flask import Flask, jsonify, render_template, request
from nlp.chatbot import ExamFAQChatbot

app = Flask(__name__)

# Initialize the NLP Chatbot engine with default threshold (0.25)
CHATBOT_ENGINE = ExamFAQChatbot(threshold=0.25)


@app.route("/")
def index():
    """Render the student chatbot interface."""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    POST /api/chat
    Input:  { "message": "When are the semester exams?" }
    Output: { "answer": "...", "confidence": 0.xx }
    """
    if not request.is_json:
        return jsonify({
            "error": "Request body must be JSON.",
            "answer": "Invalid request format.",
            "confidence": 0.0
        }), 400

    data = request.get_json(silent=True)
    if data is None or "message" not in data:
        return jsonify({
            "error": "Missing 'message' field in payload.",
            "answer": "Please provide a valid question in the message field.",
            "confidence": 0.0
        }), 400

    user_message = data.get("message", "")

    try:
        response = CHATBOT_ENGINE.get_response(user_message)
        return jsonify({
            "answer": response["answer"],
            "confidence": response["confidence"],
            "status": response.get("status", "success")
        }), 200
    except Exception as e:
        app.logger.error(f"Error processing chat request: {e}")
        return jsonify({
            "error": "Internal processing error.",
            "answer": "An error occurred while analyzing your query. Please try again.",
            "confidence": 0.0
        }), 500


@app.route("/api/info", methods=["GET"])
def info():
    """Return basic metadata about the FAQ knowledge base."""
    return jsonify({
        "title": "College Examination FAQ Chatbot",
        "category": "Examinations",
        "total_faqs": len(CHATBOT_ENGINE.faqs),
        "threshold": CHATBOT_ENGINE.threshold
    })


if __name__ == "__main__":
    # College assignment local development runner
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)

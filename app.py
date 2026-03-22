from flask import Flask, request, jsonify
import os
from google import genai

app = Flask(__name__)

# Set API key from Railway variables
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini 2.5 chat model
model = genai.ChatModel.from_name("chat-bison-002")

@app.route("/api", methods=["POST"])
def api():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_input = data["message"]
    response = model.predict(messages=[{"author": "user", "content": user_input}])

    return jsonify({"reply": response.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

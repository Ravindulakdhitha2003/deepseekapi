from flask import Flask, request, jsonify
import os
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

@app.route("/api", methods=["POST"])
def api():
    user_input = request.json.get("message")

    response = model.generate_content(user_input)

    return jsonify({
        "reply": response.text
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

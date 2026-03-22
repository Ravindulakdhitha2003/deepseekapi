from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from google import genai
import os

app = FastAPI(title="Gemini Travel Agent API")

# Allow all origins (change in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# Initialize Gemini API
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# 🔒 STRICT JSON PROMPT (ONLY for trip planning)
TRAVEL_AGENT_PROMPT = """
You are a travel planning API.

Return ONLY valid JSON.
No explanations.
No markdown.
No extra text.

Response must:
- Be valid JSON
- Start with { and end with }
- No trailing commas

Schema:
{
  "trip": [
    {
      "day": number,
      "city": string,
      "places": [
        {
          "name": string,
          "type": string,
          "imageQuery": string,
          "description": string
        }
      ]
    }
  ]
}
"""

# 💬 NORMAL CHAT PROMPT
NORMAL_CHAT_PROMPT = """
You are a helpful travel assistant.
Answer clearly and concisely in plain text.
"""

# 🧠 Intent detection
def is_trip_planning(message: str) -> bool:
    keywords = [
        "plan a trip",
        "trip plan",
        "travel plan",
        "itinerary",
        "travel itinerary",
        "day trip",
        "days trip",
        "visit places",
        "tour plan"
    ]
    msg = message.lower()
    return any(k in msg for k in keywords)

# 🩺 Health check
@app.get("/")
def health():
    return {"status": "ok"}

# 💬 Chat endpoint
@app.post("/chat")
def chat(data: ChatRequest):
    try:
        user_message = data.message
        is_trip = is_trip_planning(user_message)

        if is_trip:
            full_prompt = f"{TRAVEL_AGENT_PROMPT}\nUser request:\n{user_message}"
        else:
            full_prompt = f"{NORMAL_CHAT_PROMPT}\nUser request:\n{user_message}"

        # Gemini 2.0 Flash call using new SDK
        response = genai.chat.create(
            model="gemini-2.0-flash",
            messages=[{"author": "user", "content": full_prompt}]
        )

        return {
            "reply": response.last.content[0].text,
            "mode": "json" if is_trip else "text"
        }

    except Exception as e:
        return {
            "reply": "Sorry, something went wrong.",
            "error": str(e)
        }

# 📦 List available models
@app.get("/models")
def list_models():
    try:
        models = genai.models.list()
        return [m.name for m in models]
    except Exception as e:
        return {"error": str(e)}

# 🚀 Run locally / Railway
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

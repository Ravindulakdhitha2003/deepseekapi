from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from google import genai

app = FastAPI(title="Gemini Travel Agent API")

# Allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# Initialize Gemini client
client = genai.Client()

# 🔒 STRICT JSON PROMPT (ONLY for trip planning)
TRAVEL_AGENT_PROMPT = """
You are a travel planning API.

Return ONLY valid JSON.
No explanations.
No markdown.
No extra text.

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

# 🧠 Simple intent detection
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

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(data: ChatRequest):
    try:
        user_message = data.message

        # 🔀 Decide prompt based on intent
        if is_trip_planning(user_message):
            full_prompt = f"""
{TRAVEL_AGENT_PROMPT}

User request:
{user_message}
"""
        else:
            full_prompt = f"""
{NORMAL_CHAT_PROMPT}

User request:
{user_message}
"""





        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt
        )

        return {
            "reply": response.text,
            "mode": "json" if is_trip_planning(user_message) else "text"
        }

    except Exception as e:
        return {
            "reply": "Sorry, something went wrong.",
            "error": str(e)
        }

@app.get("/models")
def list_models():
    models = client.models.list()
    return [m.name for m in models]

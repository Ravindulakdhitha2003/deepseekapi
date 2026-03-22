from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

app = FastAPI(title="Gemini Travel Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
client = genai.Client()

TRIP_PROMPT = """You are a travel planning API. Return ONLY valid JSON, no markdown, no extra text.
Schema: {"trip":[{"day":number,"city":string,"places":[{"name":string,"type":string,"imageQuery":string,"description":string}]}]}"""

CHAT_PROMPT = "You are a helpful travel assistant. Answer clearly in plain text."

def is_trip_planning(msg: str) -> bool:
    keywords = ["plan a trip","trip plan","travel plan","itinerary","travel itinerary","day trip","days trip","visit places","tour plan"]
    return any(k in msg.lower() for k in keywords)

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(data: ChatRequest):
    try:
        trip_mode = is_trip_planning(data.message)
        prompt = f"{TRIP_PROMPT if trip_mode else CHAT_PROMPT}\n\nUser: {data.message}"
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return {"reply": response.text, "mode": "json" if trip_mode else "text"}
    except Exception as e:
        return {"reply": "Sorry, something went wrong.", "error": str(e)}

@app.get("/models")
def list_models():
    return [m.name for m in client.models.list()]


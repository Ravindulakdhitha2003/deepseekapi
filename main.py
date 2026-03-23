import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

TRIP_PROMPT = """You are a travel planning API. Return ONLY valid JSON, no markdown, no extra text.
Schema: {"trip":[{"day":number,"city":string,"places":[{"name":string,"type":string,"imageQuery":string,"description":string}]}]}"""

CHAT_PROMPT = "You are a helpful travel assistant. Answer clearly in plain text."

def is_trip(msg: str) -> bool:
    keywords = ["plan a trip","trip plan","itinerary","day trip","days trip","tour plan","visit places"]
    return any(k in msg.lower() for k in keywords)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        trip_mode = is_trip(req.message)
        prompt = f"{TRIP_PROMPT if trip_mode else CHAT_PROMPT}\n\nUser: {req.message}"
        
        # Change: model set to "gemini-1.5-flash" for Free Tier stability
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        
        return {"reply": response.text, "mode": "json" if trip_mode else "text"}
    except Exception as e:
        return {"reply": "Something went wrong.", "error": str(e)}

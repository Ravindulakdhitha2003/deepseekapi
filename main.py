import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

app = FastAPI(title="Gemini Chef API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Ensure your GEMINI_API_KEY is set in environment variables
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# ✅ CHANGED: Recipe JSON Prompt
RECIPE_PROMPT = """You are a professional chef API and food expert.

Return ONLY valid JSON when the user asks for a recipe.
Do NOT include markdown, explanations, or extra text.
Return ONLY valid JSON.
No explanations.
No markdown.
No extra text.

Schema:
{
  "recipes": [
    {
      "r_name": string,
      "category": string,
      "description": string,
      "cooking_step": string,
      "r_picture": string,
      "ingredients": [
        {
          "ingredient_name": string,
          "quantity": number,
          "unit": string,
          "calories": number,
          "carbohydrates": number,
          "protein": number,
          "fat": number,
          "clarity": string
        }
      ]
    }
  ]
}

Rules:
- r_picture must be a valid image URL of the dish.
- cooking_step must be step-by-step instructions in one string.
- Include at least 3 ingredients.
- Nutritional values must be realistic.
- STRICTLY return JSON only for recipe requests.
"""

# ✅ CHANGED: Normal Chat Prompt
CHAT_PROMPT = """You are a professional chef and food expert.

Response Style Rules:
- Keep answers SHORT and structured.
- Do NOT write long paragraphs or stories.
- Always break answers into clear sections using headings and bullet points.

Format:
- Use sections like:
  Title
  Quick Ideas / Tips / Steps
- Use bullet points or numbered lists.
- Keep each point concise (1–2 lines max).

Behavior:
- If user asks about food ideas → give 2–4 options only.
- If explaining something → keep it simple and direct.
- Avoid unnecessary details.

IMPORTANT:
- Do NOT return JSON unless the user asks for a recipe.
- Do NOT write long descriptive text.

Example Style:

Avocado Quick Ideas:

1. Avocado Toast
- Mash avocado on toast
- Add salt, pepper, chili flakes

2. Simple Salad
- Avocado + tomato
- Add olive oil + salt

3. Quick Snack
- Slice avocado
- Sprinkle salt + lemon

Keep everything clean, short, and easy to read.
"""

# ✅ CHANGED: Detection Function
def is_recipe(msg: str) -> bool:
    keywords = [
        "how to cook",
        "how to make", "how to prepare","give me recipe"
    ]
    return any(k in msg.lower() for k in keywords)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        recipe_mode = is_recipe(req.message)

        prompt = f"{RECIPE_PROMPT if recipe_mode else CHAT_PROMPT}\n\nUser: {req.message}"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return {
            "reply": response.text,
            "mode": "json" if recipe_mode else "text"
        }

    except Exception as e:
        return {
            "reply": "Something went wrong.",
            "error": str(e)
        }

import os
from google import genai

def generate_gemini_content():
    # 1. Setup - Fetch API Key from environment variables
    # Recommendation: Run `export GEMINI_API_KEY='your_key_here'` in your terminal
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("Please set the GEMINI_API_KEY environment variable.")

    # 2. Initialize the Client
    client = genai.Client(api_key=api_key)

    # 3. Generate Content
    # We're using 'gemini-2.0-flash' (standard for 2026) for speed and efficiency
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Explain the concept of 'Recursion' to a junior developer."
    )

    # 4. Output the result
    print("-" * 30)
    print("Gemini Response:")
    print("-" * 30)
    print(response.text)

if __name__ == "__main__":
    generate_gemini_content()

import os
import google.generativeai as genai

def gemini_response(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return " GEMINI_API_KEY not found"

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)

    return response.text
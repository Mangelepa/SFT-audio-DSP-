import os
import google.generativeai as genai

# Configure the Gemini API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

print("Available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)

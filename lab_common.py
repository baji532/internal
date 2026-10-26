import os
from dotenv import load_dotenv
from openai import OpenAI

# Hardcoded for fast exam execution or loaded via config
OPENAI_API_KEY = "YOUR_API_KEY_HERE"
MODEL = "gpt-4.1-mini"

client = OpenAI(api_key=OPENAI_API_KEY)

def ask(prompt, instructions="You are a helpful assistant."):
    response = client.responses.create(
        model=MODEL,
        instructions=instructions,
        input=prompt,
        max_output_tokens=1600,
    )
    if response.status == "incomplete":
        raise RuntimeError("Output was cut short. Increase the limit.")
    text = response.output_text.strip()
    if not text:
        raise RuntimeError("No text returned. Inspect the response.")
    return text

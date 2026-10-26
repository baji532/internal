from openai import OpenAI

OPENAI_API_KEY = "YOUR_API_KEY_HERE"
MODEL = "gpt-4.1-mini"

client = OpenAI(api_key=OPENAI_API_KEY)
response = client.responses.create(
    model=MODEL,
    input="Reply with exactly: Hello, world!",
    max_output_tokens=100,
)
print("Model:", MODEL)
print("Response:", response.output_text)
print("Status:", response.status)

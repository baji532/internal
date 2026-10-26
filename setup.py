import os

print("🚀 Generating all exam files automatically...")

files = {
    "lab_common.py": '''import os
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
''',

    "exp01_connectivity.py": '''from openai import OpenAI

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
''',

    "exp09_json_yaml.py": '''import json
import yaml
from openai import OpenAI

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
    return response.output_text.strip()

expected = [
    {"title": "Pride and Prejudice", "author": "Jane Austen", "year": 1813},
    {"title": "The Hobbit", "author": "J. R. R. Tolkien", "year": 1937},
    {"title": "1984", "author": "George Orwell", "year": 1949},
]
description = (
    "Pride and Prejudice; Jane Austen; 1813.\\n"
    "The Hobbit; J. R. R. Tolkien; 1937.\\n"
    "1984; George Orwell; 1949."
)

def validate(data):
    if not isinstance(data, dict) or set(data) != {"books"}:
        raise ValueError("Root must contain only the books key.")
    books = data["books"]
    if not isinstance(books, list) or len(books) != 3:
        raise ValueError("books must be a list of three records.")
    for book in books:
        if not isinstance(book, dict):
            raise ValueError("Each book must be an object.")
        if set(book) != {"title", "author", "year"}:
            raise ValueError("Incorrect book fields.")
        if not isinstance(book["title"], str):
            raise ValueError("title must be text.")
        if not isinstance(book["author"], str):
            raise ValueError("author must be text.")
        if type(book["year"]) is not int:
            raise ValueError("year must be an integer.")
    if books != expected:
        raise ValueError("Records must match the given data and order.")

for fmt, parser in [
    ("JSON", json.loads), ("YAML", yaml.safe_load)
]:
    prompt = (
        f"Convert the dataset to {fmt} only. "
        "Use a root books list. Each record has exactly "
        "title, author and year. Preserve the given order "
        "and spelling. Quote all titles and authors; "
        "years must be integers. No commentary or fences.\\n"
        "Dataset:\\n" + description
    )
    for attempt in range(2):
        raw = ask(prompt)
        try:
            parsed = parser(raw)
            validate(parsed)
        except (ValueError, TypeError, yaml.YAMLError) as error:
            if attempt == 1:
                raise
            prompt += (
                f"\\nYour previous output was:\\n{raw}\\n"
                f"Validation error: {error}\\n"
                "Correct it and return only the required format."
            )
        else:
            print("\\n" + fmt + "\\n" + raw)
            print("Syntax, structure and value checks passed.")
            break
''',

    "exp14_agent.py": '''import json
import math
from openai import OpenAI

OPENAI_API_KEY = "YOUR_API_KEY_HERE"
MODEL = "gpt-4.1-mini"
client = OpenAI(api_key=OPENAI_API_KEY)

def calculate(operation, a, b):
    if type(a) not in (int, float) or type(b) not in (int, float):
        raise ValueError("Operands must be numbers.")
    if not math.isfinite(a) or not math.isfinite(b):
        raise ValueError("Operands must be finite.")
    if operation == "add":
        value = a + b
    elif operation == "subtract":
        value = a - b
    elif operation == "multiply":
        value = a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        value = a / b
    else:
        raise ValueError("Unknown operation.")
    if not math.isfinite(value):
        raise ValueError("Result is outside the supported range.")
    return value

tool = {
    "type": "function",
    "name": "calculate",
    "description": "Calculate one binary arithmetic operation.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide"],
            },
            "a": {"type": "number"},
            "b": {"type": "number"},
        },
        "required": ["operation", "a", "b"],
        "additionalProperties": False,
    },
}

rules = (
    "Use the calculate tool for every arithmetic operation. "
    "For a multi-step expression, use each tool result "
    "in the next operation. Report errors honestly. "
    "For a non-arithmetic question, answer without a tool."
)

question = input("Question: ")
history = [{"role": "user", "content": question}]

for turn in range(8):
    response = client.responses.create(
        model=MODEL,
        instructions=rules,
        input=history,
        tools=[tool],
        parallel_tool_calls=False,
        max_output_tokens=800,
    )
    history.extend(response.output)
    calls = [item for item in response.output
             if item.type == "function_call"]
    if not calls:
        print("FINAL:", response.output_text)
        break
    for call in calls:
        try:
            if call.name != "calculate":
                raise ValueError("Tool is not permitted.")
            args = json.loads(call.arguments)
            value = calculate(**args)
            output = json.dumps({"value": value})
        except (ValueError, TypeError, OverflowError) as error:
            output = json.dumps({"error": str(error)})
        print("TOOL:", call.name, call.arguments, "=>", output)
        history.append({
            "type": "function_call_output",
            "call_id": call.call_id,
            "output": output,
        })
else:
    raise RuntimeError("Agent exceeded eight request rounds.")
'''
}

for filename, content in files.items():
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  -> Created: {filename}")

print("\\n✨ All experiment files generated successfully! You are ready.")
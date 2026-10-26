import json
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
    "Pride and Prejudice; Jane Austen; 1813.\n"
    "The Hobbit; J. R. R. Tolkien; 1937.\n"
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
        "years must be integers. No commentary or fences.\n"
        "Dataset:\n" + description
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
                f"\nYour previous output was:\n{raw}\n"
                f"Validation error: {error}\n"
                "Correct it and return only the required format."
            )
        else:
            print("\n" + fmt + "\n" + raw)
            print("Syntax, structure and value checks passed.")
            break

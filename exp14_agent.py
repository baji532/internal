import json
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

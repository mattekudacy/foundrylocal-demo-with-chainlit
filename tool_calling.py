import json
import chainlit as cl
import openai
from foundry_local import FoundryLocalManager

ALIAS = "qwen2.5-0.5b"

manager = FoundryLocalManager(ALIAS)
client = openai.OpenAI(
    base_url=manager.endpoint,
    api_key=manager.api_key,
)
MODEL_ID = manager.get_model_info(ALIAS).id

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city or location name",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit",
                    },
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A math expression using +, -, *, /, (, )",
                    }
                },
                "required": ["expression"],
            },
        },
    },
]


def get_weather(location: str, unit: str = "celsius") -> dict:
    # Simulated weather data
    temp = 22 if unit == "celsius" else 72
    return {
        "location": location,
        "temperature": temp,
        "unit": unit,
        "condition": "Sunny",
    }


def calculate(expression: str) -> dict:
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return {"error": "Invalid characters in expression"}
    try:
        result = eval(expression)  # noqa: S307 — guarded by allowlist above
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": str(e)}


TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "calculate": calculate,
}


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("messages", [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant with access to tools. "
                "Use them when needed to answer questions accurately."
            ),
        }
    ])
    await cl.Message(
        content=(
            "Hi! I'm a tool-calling assistant running locally via Foundry Local.\n\n"
            "Try asking me:\n"
            "- *What's the weather in Tokyo?*\n"
            "- *Calculate 123 * 456 + 789*"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    messages = cl.user_session.get("messages")
    messages.append({"role": "user", "content": message.content})

    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        tools=TOOLS,
    )
    choice = response.choices[0].message

    # Tool-call loop
    while choice.tool_calls:
        tool_results_text = []

        assistant_msg = {
            "role": "assistant",
            "content": choice.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in choice.tool_calls
            ],
        }
        messages.append(assistant_msg)

        for tc in choice.tool_calls:
            fn_name = tc.function.name
            args = json.loads(tc.function.arguments)
            tool_results_text.append(f"**Tool:** `{fn_name}({args})`")
            result = TOOL_FUNCTIONS[fn_name](**args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result),
            })

        # Show which tools were called as a step
        async with cl.Step(name="Tool calls") as step:
            step.output = "\n".join(tool_results_text)

        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            tools=TOOLS,
        )
        choice = response.choices[0].message

    final_answer = choice.content or ""
    messages.append({"role": "assistant", "content": final_answer})
    cl.user_session.set("messages", messages)
    await cl.Message(content=final_answer).send()

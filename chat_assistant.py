import chainlit as cl
import openai
from foundry_local import FoundryLocalManager

ALIAS = "qwen2.5-0.5b"

manager = FoundryLocalManager(ALIAS)
client = openai.AsyncOpenAI(
    base_url=manager.endpoint,
    api_key=manager.api_key,
)
MODEL_ID = manager.get_model_info(ALIAS).id


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("messages", [
        {
            "role": "system",
            "content": "You are a helpful assistant. Answer questions clearly and concisely.",
        }
    ])
    await cl.Message(content="Hello! I'm running locally via Foundry Local. How can I help you?").send()


@cl.on_message
async def on_message(message: cl.Message):
    messages = cl.user_session.get("messages")
    messages.append({"role": "user", "content": message.content})

    response_msg = cl.Message(content="")
    await response_msg.send()

    stream = await client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        stream=True,
    )

    full_response = ""
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            full_response += delta
            await response_msg.stream_token(delta)

    await response_msg.update()
    messages.append({"role": "assistant", "content": full_response})
    cl.user_session.set("messages", messages)

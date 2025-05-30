import asyncio
import os
from openai import OpenAI

from prompt import system_prompt
from tts import tts_run

OPENAI_API_KEY = ""
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = OpenAI()

messages = [
    {"role": "system", "content": system_prompt.agent_prompt},
]

def get_gpt_response(transcribed_text):
    if not transcribed_text:
        return "I didn't catch that. Could you please repeat?"

    try:
        messages.append({"role": "user", "content": transcribed_text})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
        )

        bot_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": bot_response})

        print(f"Sara 🤖: {response}")
        asyncio.run(tts_run(bot_response))

        return bot_response

    except Exception as e:
        print(f"Error getting GPT-4o mini response: {e}")
        return "Sorry, I encountered an error trying to respond."


get_gpt_response("Hello, how can I clean my floor?")
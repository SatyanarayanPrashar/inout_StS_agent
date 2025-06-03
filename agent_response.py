import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

from prompt import system_prompt
from tts import tts_run

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = AsyncOpenAI()

messages = [
    {"role": "system", "content": system_prompt.agent_prompt},
]

async def get_gpt_response(transcribed_text):
    if not transcribed_text:
        return

    request_messages = messages + [{"role": "user", "content": transcribed_text}]
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=request_messages,
        )

        bot_response = response.choices[0].message.content
        print("Sara 🤖:", bot_response)
        messages.append({"role": "assistant", "content": bot_response})
        await tts_run(bot_response)

    except Exception as e:
        print(f"Error getting GPT-4o response: {e}")

if __name__ == "__main__":
    test_text = "Hello, can you help me with your product?"
    print("Testing TTS with the following text:")
    print(test_text)
    asyncio.run(get_gpt_response(test_text))
    print("Test complete.")

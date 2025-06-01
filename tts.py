import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = AsyncOpenAI()

TTS_MODEL = "gpt-4o-mini-tts"
TTS_VOICE = "nova"
PCM_SAMPLE_RATE = 24000
PCM_CHANNELS = 1

async def play_audio_stream(audio_stream):
    try:
        with sd.OutputStream(
            samplerate=PCM_SAMPLE_RATE,
            channels=PCM_CHANNELS,
            dtype='int16'
        ) as stream:
            async for chunk in audio_stream:
                audio_array = np.frombuffer(chunk, dtype=np.int16)
                stream.write(audio_array)
    except Exception as e:
        print(f"Error playing audio stream: {e}")

async def tts_run(bot_response: str) -> None:
    if not bot_response:
        return
        
    try:
        async with client.audio.speech.with_streaming_response.create(
            model=TTS_MODEL,
            voice=TTS_VOICE,
            input=bot_response,
            response_format="pcm",
        ) as response:
            await play_audio_stream(response.iter_bytes(chunk_size=1024))
    except Exception as e:
        print(f"Error during TTS generation: {e}")

if __name__ == "__main__":
    async def main():
        test_text = "Hello, this is a test of the text to speech system."
        print("Testing TTS with the following text:")
        print(test_text)
        await tts_run(test_text)
        print("Test complete.")

    asyncio.run(main())
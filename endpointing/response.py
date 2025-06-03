import json
from openai import OpenAI

from dotenv import load_dotenv
import os

from endpoint_response import endpointing_prompt

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = OpenAI()

messages = [
    {"role": "system", "content": endpointing_prompt},
]

def endpoint_response(transcribed_text):
    if not transcribed_text:
        return

    request_messages = messages + [{"role": "user", "content": transcribed_text}]
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=request_messages,
        )

        parsed_response = json.loads(response.choices[0].message.content)
        messages.append({"role": "assistant", "content": json.dumps(parsed_response)})

        if(parsed_response.get("response") == "endpoint"):
            joined_messages = " ".join(messages[1:])
            print(f"User: ", joined_messages)


    except Exception as e:
        print(f"Error getting GPT-4o response: {e}")

# if __name__ == "__main__":
#     test_text = "me with your"
#     print(test_text)
#     endpoint_response(test_text)
#     print("Test complete.")
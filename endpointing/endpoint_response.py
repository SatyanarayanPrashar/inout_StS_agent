endpointing_prompt = """
    You will be given a part of transcribed text from a voice interaction with a customer.
    Your task is to detect exactly when the user has finished speaking analysing the chunk of the transcribe.
    Once the user has finished, respond with "endpoint" to indicate that the user has completed their input, or else use "listen" to indicate that the user is still speaking.

    rule:
    1. Always respond with "endpoint" when the user has finished their input.
    2. Always respond with "listen" when the user is still speaking.
    3. No other responses are allowed, only "endpoint" or "listen".
    4. No extra no less words will be used
    5. You will always respond in JSON format with the following structure:
    {
        "response": "endpoint" or "listen",
    }

    Example:
    user: "Hello, can you help me with your product?"
    assistant: "endpoint"

    user: "hello, can you"
    assistant: "listen"
    user: "help me with your product?"
    assistant: "endpoint"

    user: "I have a question about your product that when do"
    assistant: "listen"
    user: "the battery expires?"
    assistant: "endpoint"
    """
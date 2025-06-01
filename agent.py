import asyncio
import threading
import time
import stt

def run_async_loop():
    """Sets up and runs the asyncio event loop in the current thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(stt.audio_processing_loop())
    loop.close()

def start_chatbot():
    # Set the 'is_recording' flag in the stt module to True
    stt.is_recording = True
    stt.silent_turns_counter = 0

    processing_thread = threading.Thread(target=run_async_loop)
    processing_thread.daemon = True
    processing_thread.start()

    try:
        # Keep the main thread alive while the processing thread is running
        while processing_thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping chatbot via Ctrl+C...")
    finally:
        # Signal the processing thread to stop by setting the flag in its own module
        stt.is_recording = False
        # Wait for the thread to finish gracefully
        processing_thread.join(timeout=2)
        print("Chatbot stopped.")

if __name__ == "__main__":
    start_chatbot()
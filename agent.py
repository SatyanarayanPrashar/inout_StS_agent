import threading
import time

from stt import audio_processing_loop

def start_chatbot():
    global is_recording, silent_turns_counter
    is_recording = True
    silent_turns_counter = 0
    try:
        processing_thread = threading.Thread(target=audio_processing_loop)
        processing_thread.daemon = True
        processing_thread.start()

        while processing_thread.is_alive() and is_recording:
            time.sleep(0.5)
        
        if processing_thread.is_alive():
            processing_thread.join(timeout=2)

    except KeyboardInterrupt:
        print("\nStopping chatbot via Ctrl+C...")
        is_recording = False
        if processing_thread.is_alive():
            processing_thread.join(timeout=2)
    finally:
        is_recording = False
        print("Chatbot stopped.")

if __name__ == "__main__":
    start_chatbot()
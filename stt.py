import sounddevice as sd
import numpy as np
import wave
from openai import OpenAI
import os
import time

from agent_response import get_gpt_response
from tts import tts_run

OPENAI_API_KEY = ""
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = OpenAI()

SAMPLE_RATE = 16000
CHANNELS = 1
SILENCE_THRESHOLD = 700
SILENCE_DURATION_SECONDS = 5
RECORDING_CHUNK_SECONDS = 1
MAX_SILENT_TURNS = 2

is_recording = False
audio_frames = []
last_speech_time = time.time()
silent_turns_counter = 0

def record_audio_chunk(stream):
    global audio_frames, last_speech_time
    try:
        audio_chunk, overflowed = stream.read(int(SAMPLE_RATE * RECORDING_CHUNK_SECONDS))
        # if overflowed:
        #     print("Warning: Input overflowed!")

        audio_frames.append(audio_chunk)

        if audio_chunk.size > 0:
            rms = np.sqrt(np.mean(audio_chunk.astype(np.float32)**2))
            if rms > SILENCE_THRESHOLD:
                last_speech_time = time.time()
        return True
    except sd.PortAudioError as e:
        print(f"PortAudioError reading from stream: {e}")
        return False
    except Exception as e:
        print(f"Generic error reading from stream: {e}")
        return False

def save_recorded_audio(processed_audio_data_int16, filename="temp_audio.wav"):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2) # 2 bytes for int16
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(processed_audio_data_int16.tobytes())
    wf.close()
    return filename

def transcribe_audio_whisper(audio_file_path):
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcription.text
    except Exception as e:
        print(f"Error during Whisper transcription: {e}")
        return None

def audio_processing_loop():
    global is_recording, audio_frames, last_speech_time, silent_turns_counter
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16',
                        blocksize=int(SAMPLE_RATE * RECORDING_CHUNK_SECONDS)) as stream:
        print("Listening... (Press Ctrl+C to stop)")
        is_recording = True
        last_speech_time = time.time()

        while is_recording:
            if not record_audio_chunk(stream):
                time.sleep(0.1)
                continue

            if time.time() - last_speech_time > SILENCE_DURATION_SECONDS:
                if not audio_frames:
                    print("No audio frames accumulated during silence period. Skipping processing.")
                    last_speech_time = time.time()
                    silent_turns_counter += 1
                    if is_recording and silent_turns_counter >= MAX_SILENT_TURNS:
                        print(f"Stopping chatbot after {MAX_SILENT_TURNS} consecutive silent turns.")
                        is_recording = False
                    continue

                concatenated_audio_int16 = np.concatenate(audio_frames)
                audio_float32 = concatenated_audio_int16.astype(np.float32) / 32768.0

                MIN_AUDIO_LENGTH_SAMPLES = int(SAMPLE_RATE * 1.5)

                if len(audio_float32) < MIN_AUDIO_LENGTH_SAMPLES or np.allclose(audio_float32, 0, atol=1e-5):
                    print(f"Audio too short ({len(audio_float32)} samples) or silent. Skipping transcription.")
                    silent_turns_counter += 1
                    print(f"No speech detected. Silent turn count: {silent_turns_counter}/{MAX_SILENT_TURNS}")
                    if is_recording and silent_turns_counter >= MAX_SILENT_TURNS:
                        print(f"Stopping chatbot after {MAX_SILENT_TURNS} consecutive silent turns.")
                        is_recording = False
                else:
                    reduced_noise_int16 = (audio_float32 * 32768.0).astype(np.int16)
                    temp_audio_file = save_recorded_audio(reduced_noise_int16)
                    transcribed_text = transcribe_audio_whisper(temp_audio_file)
                    print(f"You: {transcribed_text}")

                    if transcribed_text and len(transcribed_text.strip().split()) > 2:
                        response = get_gpt_response(transcribed_text)
                        silent_turns_counter = 0
                    else:
                        print("Chatbot: Sorry, I couldn't understand the audio or detected only silence.")
                        silent_turns_counter += 1
                        print(f"No meaningful speech. Silent turn count: {silent_turns_counter}/{MAX_SILENT_TURNS}")

                    try:
                        os.remove(temp_audio_file)
                    except OSError as e:
                        print(f"Error deleting temp file: {e}")
                    
                    if is_recording and silent_turns_counter < MAX_SILENT_TURNS:
                        print("\nListening...")
                
                audio_frames = [] 
                last_speech_time = time.time()

                if silent_turns_counter >= MAX_SILENT_TURNS:
                    print(f"Stopping chatbot after {MAX_SILENT_TURNS} consecutive silent turns.")
                    is_recording = False
            
            if is_recording:
                time.sleep(0.05)

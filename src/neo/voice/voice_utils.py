"""Voice utilities for audio recording, transcription, and text-to-speech."""

import asyncio
import io
import threading
import wave
from typing import Optional

import numpy as np
import sounddevice as sd
from openai import OpenAI
from scipy.io import wavfile


# Initialize OpenAI client
client = OpenAI()

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1


def record_audio_until_stop() -> Optional[bytes]:
    """
    Record audio until the user presses Enter.
    
    Returns:
        bytes: WAV audio data or None if recording failed
    """
    print("Recording... Press Enter to stop.")
    
    recording = []
    stop_recording = threading.Event()
    
    def audio_callback(indata, frames, time, status):
        if status:
            print(f"Audio callback status: {status}")
        recording.append(indata.copy())
    
    def wait_for_enter():
        input()
        stop_recording.set()
    
    # Start recording
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        callback=audio_callback,
        dtype=np.float32
    ):
        # Start thread to wait for Enter key
        enter_thread = threading.Thread(target=wait_for_enter)
        enter_thread.start()
        
        # Wait for Enter key
        stop_recording.wait()
        enter_thread.join()
    
    print("Recording stopped.")
    
    if not recording:
        print("No audio recorded.")
        return None
    
    # Convert to numpy array
    audio_data = np.concatenate(recording, axis=0)
    
    # Convert float32 to int16 for WAV format
    audio_int16 = (audio_data * 32767).astype(np.int16)
    
    # Create WAV file in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)  # 2 bytes for int16
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio_int16.tobytes())
    
    wav_buffer.seek(0)
    return wav_buffer.read()


def transcribe_audio(audio_data: bytes) -> str:
    """
    Transcribe audio data to text using OpenAI Whisper.
    
    Args:
        audio_data: WAV audio data as bytes
        
    Returns:
        str: Transcribed text
    """
    try:
        # Create a file-like object from bytes
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "recording.wav"  # Whisper needs a filename
        
        # Use OpenAI Whisper API
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        
        return transcript.text.strip()
    
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""


def play_audio(text: str) -> None:
    """
    Convert text to speech and play it using OpenAI TTS.
    
    Args:
        text: Text to convert to speech
    """
    if not text.strip():
        return
    
    try:
        print("Generating speech...")
        
        # Generate speech using OpenAI TTS (MP3 format is more reliable)
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="fable",
            input=text,
            response_format="mp3"
        )
        
        # Get audio bytes and save to temporary file
        audio_bytes = response.content
        
        # Save to temporary file and read with soundfile
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        try:
            # Use sounddevice to play the file directly
            import soundfile as sf
            audio_data, sample_rate = sf.read(temp_path)
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
        
        # Normalize audio data if needed
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32767.0
        elif audio_data.dtype == np.int32:
            audio_data = audio_data.astype(np.float32) / 2147483647.0
        
        print("Playing response...")
        
        # Play audio
        sd.play(audio_data, sample_rate)
        sd.wait()  # Wait until playback is finished
        
        print("Playback complete.")
        
    except Exception as e:
        print(f"TTS error: {e}")
        print(f"Fallback text: {text}")


async def record_audio_until_stop_async() -> Optional[bytes]:
    """Async wrapper for record_audio_until_stop."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, record_audio_until_stop)


async def transcribe_audio_async(audio_data: bytes) -> str:
    """Async wrapper for transcribe_audio."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, transcribe_audio, audio_data)


async def play_audio_async(text: str) -> None:
    """Async wrapper for play_audio."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, play_audio, text)
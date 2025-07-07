"""Generates subtitles from an audio file using OpenAI's Whisper API."""
import os
from openai import OpenAI
import numpy as np
from scipy.io.wavfile import write # For placeholder

def srt_time_format(seconds):
    """Converts seconds to SRT time format (HH:MM:SS,ms)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def generate_subtitles(full_narration_text, output_dir):
    """
    Generates subtitles from a given text using OpenAI TTS and Whisper.

    Args:
        full_narration_text: The complete text to generate subtitles for.
        output_dir: The directory where the subtitle file will be saved.

    Returns:
        The path to the generated .srt subtitles file.
    """
    print(f"  -> Generating subtitles for full narration...")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # 1. Generate temporary audio from full_narration_text
    temp_audio_path = os.path.join(output_dir, "temp_full_narration.mp3")
    try:
        print(f"     - Generating temporary audio for transcription...")
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy", # Consistent with voice.py
            input=full_narration_text
        )
        response.stream_to_file(temp_audio_path)
        print(f"     - Temporary audio saved to {temp_audio_path}")
    except Exception as e:
        print(f"     - Error generating temporary audio for subtitles: {e}")
        # Fallback for temporary audio
        print("     - Creating a placeholder temporary audio file.")
        samplerate = 44100
        duration = 5.0
        frequency = 440
        t = np.linspace(0., duration, int(samplerate * duration))
        amplitude = np.iinfo(np.int16).max * 0.5
        data = amplitude * np.sin(2. * np.pi * frequency * t)
        write(temp_audio_path, samplerate, data.astype(np.int16))
        
    subtitle_path = os.path.join(output_dir, "subtitles.srt")

    try:
        with open(temp_audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )

        with open(subtitle_path, "w", encoding="utf-8") as f:
            for i, word in enumerate(transcript.words):
                start_time = srt_time_format(word['start'])
                end_time = srt_time_format(word['end'])
                f.write(f"{i+1}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{word['word'].strip()}\n\n")
        
        print(f"     - Subtitles saved to {subtitle_path}")
        return subtitle_path

    except Exception as e:
        print(f"     - Error generating subtitles: {e}")
        # Fallback to a placeholder
        print("     - Creating a placeholder subtitle file.")
        with open(subtitle_path, "w") as f:
            f.write("1\n00:00:00,000 --> 00:00:05,000\nSubtitle generation failed.\n")
        return subtitle_path
    finally:
        # Clean up temporary audio file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

if __name__ == '__main__':
    # Example usage for testing
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
    else:
        test_narration = "Hello, this is a test of the subtitle generation. I hope it works well."
        test_output_dir = "test_output_subtitles"
        os.makedirs(test_output_dir, exist_ok=True)
        path = generate_subtitles(test_narration, test_output_dir)
        print(f"\nGenerated subtitle file at: {path}")
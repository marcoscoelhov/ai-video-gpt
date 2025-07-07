"""Generates audio from text using gTTS, creating separate audio files for each scene's narration."""
import os
from gtts import gTTS

def tts_scenes(script_data, output_dir):
    """
    Generates audio for each scene's narration using gTTS.

    Args:
        script_data: A dictionary representing the structured script.
        output_dir: The directory where audio files will be saved.

    Returns:
        A list of paths to the generated audio files, one for each scene.
    """
    audio_paths = []

    if not isinstance(script_data, dict) or "scenes" not in script_data:
        print("Error: Invalid script format. Expected a dictionary with a 'scenes' key.")
        return []

    for i, scene in enumerate(script_data["scenes"]):
        narration_text = scene.get("narration")
        if not narration_text:
            print(f"Warning: Scene {scene.get('scene', '?')} is missing narration text. Skipping audio generation for this scene.")
            continue

        audio_path = os.path.join(output_dir, f"audio_scene_{i+1:02d}.mp3")
        print(f"  -> Generating audio for scene {i+1}: '{narration_text[:50]}...' ")

        try:
            tts = gTTS(text=narration_text, lang='en') # You can change 'en' to 'pt' for Portuguese
            tts.save(audio_path)
            audio_paths.append(audio_path)
            print(f"     - Audio saved to {audio_path}")

        except Exception as e:
            print(f"     - Error generating audio for scene {i+1}: {e}")

    return audio_paths

if __name__ == '__main__':
    # Example usage for testing
    test_script = {
      "theme": "The secret life of garden gnomes",
      "title": "Gnome Sweet Gnome",
      "scenes": [
        {
          "scene": 1,
          "visual_description": "digital comic book art of a garden gnome secretly polishing his fishing rod at midnight, with the moon shining brightly.",
          "narration": "At night, the garden reveals its secrets."
        },
        {
          "scene": 2,
          "visual_description": "digital comic book art of two gnomes playing a high-stakes game of poker on a toadstool table.",
          "narration": "Bernard was all in, but Gerald held the winning hand."
        }
      ]
    }
    
    # For testing, create a dummy output directory
    test_output_dir = "test_output_audio"
    os.makedirs(test_output_dir, exist_ok=True)
    generated_audio_paths = tts_scenes(test_script, test_output_dir)
    print("\n--- Generated Audio Paths ---")
    for p in generated_audio_paths:
        print(f"- {p}")
    print("-----------------------------")

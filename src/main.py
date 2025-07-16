
import argparse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from scriptgen import generate_script
from prompt import scene_prompts
from imagegen import generate_images_from_prompts
from voice import tts_scenes
from subtitle import generate_subtitles
from assemble import assemble_video

def main(theme):
    """
    Main function to generate a video from a theme.
    """
    print(f"Starting video generation for theme: '{theme}'")

    # Create output directory if it doesn't exist
    if not os.path.exists("output"):
        os.makedirs("output")

    # Step 1: Generate script
    print("\n📝 Step 1: Generating script...")
    script = generate_script(theme)
    print(f"   -> Script generated successfully.")

    # Step 2: Generate image prompts
    print("\n🎨 Step 2: Generating image prompts...")
    prompts = scene_prompts(script)
    print(f"   -> {len(prompts)} prompts generated.")

    # Step 3: Generate images
    print("\n🖼️ Step 3: Generating images...")
    image_paths = generate_images_from_prompts(prompts, "output")
    if not image_paths:
        print("   -> Image generation failed. Aborting.")
        return
    print(f"   -> {len(image_paths)} images generated successfully.")

    # Step 4: Generate audio
    print("\n🎙️ Step 4: Generating audio...")
    audio_paths = tts_scenes(script, "output")
    if not audio_paths:
        print("   -> Audio generation failed. Aborting.")
        return
    print(f"   -> {len(audio_paths)} audio files generated successfully.")

    # Step 5: Generate subtitles
    print("\n📝 Step 5: Generating subtitles...")
    subtitle_path = generate_subtitles(audio_paths, "output")
    if not subtitle_path:
        print("   -> Subtitle generation failed. Aborting.")
        return
    print(f"   -> Subtitles generated at: {subtitle_path}")

    # Step 6: Assemble video
    print("\n🎬 Step 6: Assembling video...")
    video_path = assemble_video(image_paths, audio_paths, subtitle_path, "output/final_video.mp4")
    if video_path:
        print(f"\n✅ Video successfully assembled at: {video_path}")
    else:
        print("\nVideo assembly failed. Check logs for errors, especially for ffmpeg/ffprobe installation.")

if __name__ == "__main__":
    # Hardcode theme for testing purposes due to shell argument parsing issues
    fixed_theme = "The secret life of garden gnomes"

    # Check for API keys
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY must be set in your .env file.")
    else:
        main(fixed_theme)

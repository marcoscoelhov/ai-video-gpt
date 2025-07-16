import argparse
import os
import sys
import json
import datetime
from dotenv import load_dotenv

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

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
    print(f"🎬 Starting video generation for theme: '{theme}'")

    # Generate a unique ID for this video run
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_id = f"video_{theme.replace(' ', '_').lower()}_{timestamp}"
    video_output_dir = os.path.join("output", video_id)

    # Create output directories
    os.makedirs(video_output_dir, exist_ok=True)
    os.makedirs(os.path.join(video_output_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(video_output_dir, "audio"), exist_ok=True)
    os.makedirs(os.path.join(video_output_dir, "subtitles"), exist_ok=True)

    print(f"   -> Output will be saved to: {video_output_dir}")

    # Step 1: Generate structured script
    print("\n📝 Step 1: Generating structured script...")
    script_data = generate_script(theme)
    if not script_data:
        print("   -> Script generation failed. Aborting.")
        return
    
    # Save the structured script
    script_path = os.path.join(video_output_dir, "script.json")
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)
    print(f"   -> Structured script saved to: {script_path}")

    # Step 2: Generate image prompts from structured script
    print("\n🎨 Step 2: Generating image prompts...")
    prompts = scene_prompts(script_data)
    if not prompts:
        print("   -> No image prompts generated. Aborting.")
        return
    print(f"   -> {len(prompts)} prompts extracted from script.")

    # Step 3: Generate images
    print("\n🖼️ Step 3: Generating images...")
    # Pass the image output directory to imagegen
    image_output_dir = os.path.join(video_output_dir, "images")
    image_paths = generate_images_from_prompts(prompts, image_output_dir)
    if not image_paths:
        print("   -> Image generation failed. Aborting.")
        return
    print(f"   -> {len(image_paths)} images generated successfully.")

    # Step 4: Generate audio for each scene
    print("\n🎙️ Step 4: Generating audio...")
    # Pass the audio output directory to voice
    audio_output_dir = os.path.join(video_output_dir, "audio")
    audio_paths = tts_scenes(script_data, audio_output_dir)
    if not audio_paths:
        print("   -> Audio generation failed. Aborting.")
        return
    print(f"   -> {len(audio_paths)} audio files generated successfully.")

    # Step 5: Generate subtitles using Gemini 2.0 Flash
    print("\n📜 Step 5: Generating subtitles...")
    # Use the generated audio files to create subtitles with Gemini
    subtitle_output_dir = os.path.join(video_output_dir, "subtitles")
    subtitle_path = generate_subtitles(audio_paths, subtitle_output_dir)
    if not subtitle_path:
        print("   -> Subtitle generation failed. Aborting.")
        return
    print(f"   -> Subtitles generated at: {subtitle_path}")

    # Step 6: Assemble video
    print("\n🎞️ Step 6: Assembling video...")
    # Pass all generated image and audio paths, and the final video output path
    final_video_path = os.path.join(video_output_dir, f"{video_id}.mp4")
    video_path = assemble_video(image_paths, audio_paths, subtitle_path, final_video_path)
    if video_path:
        print(f"\n✅ Video successfully assembled at: {video_path}")
    else:
        print("\n❌ Video assembly failed. Check logs for errors, especially for ffmpeg/ffprobe installation.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a short AI comic-style video from a theme.")
    parser.add_argument("--theme", type=str, help="The theme of the video (e.g., 'Cyberpunk city exploration').")
    parser.add_argument("--test", action="store_true", help="Run in test mode using existing files (no API calls)")
    args = parser.parse_args()

    # Test mode - use existing files
    if args.test:
        print("🧪 Executando em modo de teste...")
        print("💡 Use: python test_mode.py --list para ver projetos disponíveis")
        print("💡 Use: python test_mode.py --project <nome> para testar montagem")
        sys.exit(0)
    
    # Normal mode - require theme
    if not args.theme:
        parser.error("--theme é obrigatório no modo normal. Use --test para modo de teste.")

    # Check for API keys
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY must be set in your .env file.")
        print("Note: OPENAI_API_KEY is optional (only needed for voice generation if using OpenAI TTS)")
    elif not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found. Voice generation may fail if using OpenAI TTS.")
        print("Continuing with Gemini for image generation and subtitles...")
        main(args.theme)
    else:
        main(args.theme)
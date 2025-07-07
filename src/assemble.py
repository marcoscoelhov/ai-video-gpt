import subprocess
import os
import json

def get_audio_duration(audio_path):
    """Gets the duration of an audio file using ffprobe."""
    command = [
        os.getenv("FFPROBE_PATH", "ffprobe"),
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return float(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error getting audio duration with ffprobe: {e}")
        print("Please ensure ffprobe is installed and in your system's PATH.")
        return 0.0 # Return 0.0 if duration cannot be determined

def concatenate_audios(audio_paths, output_path):
    """
    Concatenates multiple audio files into a single one using FFmpeg.
    """
    if not audio_paths:
        return None

    ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")
    
    # Create a temporary file listing audio files for concatenation
    audio_list_path = "temp_audio_list.txt"
    with open(audio_list_path, "w") as f:
        for ap in audio_paths:
            f.write(f"file '{os.path.abspath(ap)}'\n")

    command = [
        ffmpeg_path,
        "-f", "concat",
        "-safe", "0",
        "-i", audio_list_path,
        "-c", "copy",
        output_path
    ]

    print(f"  -> Concatenating audio files to {output_path}...")
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"     - Audio concatenation successful.")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"     - Error during audio concatenation: {e.stderr}")
        return None
    finally:
        if os.path.exists(audio_list_path):
            os.remove(audio_list_path)

def assemble_video(image_paths, audio_paths, subtitle_path, final_video_path):
    """
    Assembles a video from a list of images, a list of audio files (one per image/scene),
    and a subtitle file.
    """
    if not image_paths or not audio_paths or len(image_paths) != len(audio_paths):
        print("Error: Mismatch in number of images and audio files, or no files provided.")
        return None

    ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")
    
    # 1. Concatenate all audio files into a single temporary audio file
    concatenated_audio_path = os.path.join(os.path.dirname(final_video_path), "temp_concatenated_audio.mp3")
    concatenated_audio = concatenate_audios(audio_paths, concatenated_audio_path)
    if not concatenated_audio:
        print("Error: Failed to concatenate audio files.")
        return None

    # 2. Create a temporary file for ffmpeg image input with durations
    image_input_list_path = os.path.join(os.path.dirname(final_video_path), "temp_image_input.txt")
    with open(image_input_list_path, "w") as f:
        for i, img_path in enumerate(image_paths):
            duration = get_audio_duration(audio_paths[i])
            if duration == 0.0:
                print(f"Warning: Audio duration for {audio_paths[i]} is 0. Using default 5 seconds.")
                duration = 5.0 # Fallback for images if audio duration is 0
            f.write(f"file '{os.path.abspath(img_path)}'\n")
            f.write(f"duration {duration}\n")
        # Add the last image again without duration to ensure it's displayed for its full duration
        f.write(f"file '{os.path.abspath(image_paths[-1])}'\n")

    # 3. Build the ffmpeg command
    command = [
        ffmpeg_path,
        "-f", "concat",
        "-safe", "0",
        "-i", image_input_list_path,
        "-i", concatenated_audio,
        "-vf", f"scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p,subtitles={os.path.abspath(subtitle_path)}",
        "-c:v", "libx264",
        "-preset", "medium",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest", # Ensures video length matches audio length
        "-y", # Overwrite output file if it exists
        final_video_path
    ]

    print(f"  -> Assembling video to {final_video_path}...")
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"     - Video assembled successfully.")
        return final_video_path
    except subprocess.CalledProcessError as e:
        print(f"     - Error during video assembly: {e.stderr}")
        return None
    finally:
        # Clean up temporary files
        if os.path.exists(concatenated_audio_path):
            os.remove(concatenated_audio_path)
        if os.path.exists(image_input_list_path):
            os.remove(image_input_list_path)

if __name__ == '__main__':
    # Example usage for testing
    # This part needs dummy files to run
    print("Please provide dummy image and audio files in 'output/' for testing assemble.py")
    print("Example: python assemble.py image1.png audio1.mp3 image2.png audio2.mp3 output/final.mp4")
    # For a full test, run main.py after all refactoring is done.
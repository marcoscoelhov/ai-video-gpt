import subprocess
import os
import json
from .subtitle_styles import SubtitleStyleManager, SubtitleStyle
from ..utils.security import (
    validate_file_path, validate_directory_path, safe_subprocess_run,
    get_safe_env_path, create_temp_file_list, cleanup_temp_files,
    SecurityError
)

def get_audio_duration(audio_path):
    """Gets the duration of an audio file using ffprobe."""
    try:
        # Validate input file path
        validated_audio_path = validate_file_path(audio_path, must_exist=True, 
                                                allowed_extensions=['.mp3', '.wav', '.m4a', '.aac', '.ogg'])
        
        # Get secure ffprobe path
        ffprobe_path = get_safe_env_path("FFPROBE_PATH", "ffprobe")
        
        # Build secure command
        command = [
            ffprobe_path,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            validated_audio_path
        ]
        
        result = safe_subprocess_run(command, timeout=30)
        return float(result.stdout.strip())
        
    except (SecurityError, ValueError) as e:
        print(f"Error getting audio duration: {e}")
        return 0.0

def concatenate_audios(audio_paths, output_path):
    """
    Concatenates multiple audio files into a single one using FFmpeg.
    """
    if not audio_paths:
        return None

    try:
        # Validate all input audio files
        validated_audio_paths = []
        for ap in audio_paths:
            validated_audio_paths.append(validate_file_path(ap, must_exist=True, 
                                                          allowed_extensions=['.mp3', '.wav', '.m4a', '.aac', '.ogg']))
        
        # Validate output path
        output_dir = os.path.dirname(output_path)
        if output_dir:
            validate_directory_path(output_dir, create_if_not_exists=True)
        validated_output_path = validate_file_path(output_path)
        
        # Get secure ffmpeg path
        ffmpeg_path = get_safe_env_path("FFMPEG_PATH", "ffmpeg")
        
        # Create secure temporary file list
        audio_list_path = create_temp_file_list(validated_audio_paths, output_dir or os.getcwd())

        command = [
            ffmpeg_path,
            "-f", "concat",
            "-safe", "0",
            "-i", audio_list_path,
            "-c", "copy",
            validated_output_path
        ]

        print(f"  -> Concatenating audio files to {validated_output_path}...")
        
        result = safe_subprocess_run(command, timeout=300)
        print(f"     - Audio concatenation successful.")
        return validated_output_path
        
    except SecurityError as e:
        print(f"     - Security error during audio concatenation: {e}")
        return None
    except Exception as e:
        print(f"     - Error during audio concatenation: {e}")
        return None
    finally:
        if 'audio_list_path' in locals():
            cleanup_temp_files(audio_list_path)

def assemble_video(image_paths, audio_paths, subtitle_path, final_video_path, subtitle_style="modern"):
    """
    Assembles a video from a list of images, a list of audio files (one per image/scene),
    and a subtitle file with professional styling.
    
    Args:
        image_paths: List of image file paths
        audio_paths: List of audio file paths
        subtitle_path: Path to subtitle file
        final_video_path: Output video path
        subtitle_style: Style name or SubtitleStyle object ('netflix', 'youtube', 'cinema', 'modern', 'accessibility')
    """
    if not image_paths or not audio_paths or len(image_paths) != len(audio_paths):
        print("Error: Mismatch in number of images and audio files, or no files provided.")
        return None

    try:
        # Validate all input files
        validated_image_paths = []
        for img_path in image_paths:
            validated_image_paths.append(validate_file_path(img_path, must_exist=True,
                                                          allowed_extensions=['.png', '.jpg', '.jpeg', '.bmp', '.tiff']))
        
        validated_audio_paths = []
        for audio_path in audio_paths:
            validated_audio_paths.append(validate_file_path(audio_path, must_exist=True,
                                                          allowed_extensions=['.mp3', '.wav', '.m4a', '.aac', '.ogg']))
        
        # Validate output path
        output_dir = os.path.dirname(final_video_path)
        if output_dir:
            validate_directory_path(output_dir, create_if_not_exists=True)
        validated_final_video_path = validate_file_path(final_video_path)
        
        # Validate subtitle path if provided
        validated_subtitle_path = None
        if subtitle_path and os.path.exists(subtitle_path):
            validated_subtitle_path = validate_file_path(subtitle_path, must_exist=True,
                                                       allowed_extensions=['.srt', '.ass', '.vtt'])
        
        # Get secure ffmpeg path
        ffmpeg_path = get_safe_env_path("FFMPEG_PATH", "ffmpeg")
        
        # Create temporary file paths
        temp_subtitle_path = None
        if validated_subtitle_path:
            temp_subtitle_path = os.path.join(output_dir or os.getcwd(), "temp_subs.srt")
            # Securely copy subtitle file
            import shutil
            shutil.copy2(validated_subtitle_path, temp_subtitle_path)
        
        # 1. Concatenate all audio files into a single temporary audio file
        concatenated_audio_path = os.path.join(output_dir or os.getcwd(), "temp_concatenated_audio.mp3")
        concatenated_audio = concatenate_audios(validated_audio_paths, concatenated_audio_path)
        if not concatenated_audio:
            print("Error: Failed to concatenate audio files.")
            return None

        # 2. Create a temporary file for ffmpeg image input with durations
        durations_and_paths = []
        for i, img_path in enumerate(validated_image_paths):
            duration = get_audio_duration(validated_audio_paths[i])
            if duration == 0.0:
                print(f"Warning: Audio duration for {validated_audio_paths[i]} is 0. Using default 5 seconds.")
                duration = 5.0
            durations_and_paths.append((img_path, duration))
        
        # Create secure image list file
        image_input_list_path = create_temp_file_list(
            [img_path for img_path, _ in durations_and_paths], 
            output_dir or os.getcwd()
        )
        
        # Add duration information to the file
        with open(image_input_list_path, "w", encoding='utf-8') as f:
            for img_path, duration in durations_and_paths:
                # Use forward slashes for ffmpeg compatibility and escape quotes
                ffmpeg_path_safe = img_path.replace('\\', '/').replace("'", "\\'")
                f.write(f"file '{ffmpeg_path_safe}'\n")
                f.write(f"duration {duration}\n")
            # Add the last image again without duration
            if durations_and_paths:
                last_img = durations_and_paths[-1][0].replace('\\', '/').replace("'", "\\'")
                f.write(f"file '{last_img}'\n")

        # 3. Build the ffmpeg command
        command = [
            ffmpeg_path,
            "-f", "concat",
            "-safe", "0",
            "-i", image_input_list_path,
            "-i", concatenated_audio,
            "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p",
            "-c:v", "libx264",
            "-preset", "medium",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",  # Ensures video length matches audio length
            "-y",  # Overwrite output file if it exists
            validated_final_video_path
        ]
        
        print(f"  -> Assembling video to {validated_final_video_path}...")
        
        # Check if we need to add subtitles
        if temp_subtitle_path and os.path.exists(temp_subtitle_path):
            # Create a temporary video first, then add subtitles
            temp_video_path = validated_final_video_path.replace('.mp4', '_temp.mp4')
            
            # First pass: create video without subtitles
            try:
                result = safe_subprocess_run(command[:-1] + [temp_video_path], timeout=600)
                print(f"     - Base video created successfully.")
                
                # Second pass: burn subtitles with professional styling
                if isinstance(subtitle_style, str):
                    style_config = SubtitleStyleManager.get_style(subtitle_style)
                else:
                    style_config = subtitle_style
                
                # Detect video format based on filename or dimensions
                video_format = "standard"
                if "tiktok" in validated_final_video_path.lower() or "9:16" in validated_final_video_path.lower():
                    video_format = "tiktok"
                elif "youtube" in validated_final_video_path.lower():
                    video_format = "youtube"
                
                # Generate styled subtitle filter
                subtitle_filter = SubtitleStyleManager.generate_ffmpeg_subtitle_filter(
                    style_config, temp_subtitle_path, video_format
                )
                
                subtitle_command = [
                    ffmpeg_path,
                    "-i", temp_video_path,
                    "-vf", subtitle_filter,
                    "-c:a", "copy",
                    "-y",
                    validated_final_video_path
                ]
                
                result = safe_subprocess_run(subtitle_command, timeout=600)
                print(f"     - Subtitles added successfully.")
                
            except SecurityError as e:
                print(f"     - Security error during video assembly with subtitles: {e}")
                # If subtitle burning fails, rename temp video to final (if it exists)
                if os.path.exists(temp_video_path):
                    os.rename(temp_video_path, validated_final_video_path)
                    print(f"     - Video created without subtitles.")
                else:
                    return None
            finally:
                # Clean up temp video
                if os.path.exists(temp_video_path):
                    cleanup_temp_files(temp_video_path)
        else:
            # No subtitles, create video directly
            try:
                result = safe_subprocess_run(command, timeout=600)
            except SecurityError as e:
                print(f"     - Security error during video assembly: {e}")
                return None
        
        print(f"     - Video assembled successfully.")
        return validated_final_video_path
        
    except SecurityError as e:
        print(f"Error: Security validation failed - {e}")
        return None
    except Exception as e:
        print(f"Error: Unexpected error during video assembly - {e}")
        return None
    finally:
        # Clean up temporary files
        cleanup_temp_files(
            concatenated_audio_path if 'concatenated_audio_path' in locals() else None,
            image_input_list_path if 'image_input_list_path' in locals() else None,
            temp_subtitle_path if 'temp_subtitle_path' in locals() else None
        )

if __name__ == '__main__':
    # Example usage for testing
    # This part needs dummy files to run
    print("Please provide dummy image and audio files in 'outputs/videos/' for testing assemble.py")
    print("Example: python assemble.py image1.png audio1.mp3 image2.png audio2.mp3 outputs/videos/final.mp4")
    # For a full test, run main.py after all refactoring is done.
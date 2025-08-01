"""Generates a structured video script in JSON format using the Gemini API."""
import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Import logging
from src.utils.logger import get_logger, log_api_call, log_performance

# Load environment variables and configure API
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@log_performance("script_generation")
def generate_script(theme):
    """
    Generates a structured script with a title and scenes based on a theme.

    Args:
        theme: The theme of the video.

    Returns:
        A dictionary representing the structured script, or None if generation fails.
    """
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    prompt = f"""
    You are a creative writer for short, viral videos.
    Based on the theme '{theme}', create a compelling script with a catchy title and 3 to 4 distinct scenes.
    The total narration across all scenes must be less than 90 words.

    Your response MUST be a single, valid JSON object. Do not add any text, comments, or explanations before or after the JSON.

    The JSON object must have this exact structure:
    {{
      "theme": "The original theme provided",
      "title": "A catchy title for the video",
      "scenes": [
        {{
          "scene": 1,
          "visual_description": "A detailed visual description for an AI image generator. The style should be vibrant, cinematic, digital comic book art.",
          "narration": "A short, engaging sentence for the voice-over for this scene."
        }},
        {{
          "scene": 2,
          "visual_description": "...",
          "narration": "..."
        }}
      ]
    }}

    Theme: "{theme}"
    """

    logger = get_logger("core.scriptgen")
    logger.info(f"Generating structured script for theme: '{theme}'", extra={'extra_data': {'theme': theme}})
    
    try:
        log_api_call("gemini", "generate_content", {'theme': theme, 'model': 'gemini-1.5-pro-latest'})
        response = model.generate_content(prompt)
        
        # Clean the response to extract only the JSON part
        # The model might wrap the JSON in ```json ... ```
        text_response = response.text.strip()
        match = re.search(r'```json\n(.*?)\n```', text_response, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_str = text_response

        # Parse the JSON string into a Python dictionary
        script_data = json.loads(json_str)
        logger.info("Structured script generated successfully", extra={'extra_data': {'scenes_count': len(script_data.get('scenes', []))}})
        return script_data

    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Error generating or parsing structured script: {e}", extra={'extra_data': {'theme': theme, 'error_type': type(e).__name__}})
        if 'response' in locals():
            logger.debug(f"Raw response from model: {response.text}")
        return None

if __name__ == '__main__':
    # Setup logging for testing
    from src.utils.logger import setup_logging
    setup_logging(log_level="DEBUG")
    logger = get_logger("core.scriptgen.test")
    
    # Example usage for testing
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY environment variable not set")
    else:
        test_theme = "The secret life of garden gnomes"
        generated_script = generate_script(test_theme)
        if generated_script:
            logger.info("Generated Script:", extra={'extra_data': generated_script})
            print(json.dumps(generated_script, indent=2))  # Keep print for testing output
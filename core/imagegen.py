"""Generates images from prompts using Google Gemini 2.0 Flash."""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cost_tracker import CostTracker
from config.gemini_imagen_client import GeminiImagenClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_gemini_client():
    """Initialize Gemini client with API key from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    try:
        client = GeminiImagenClient(api_key=api_key)
        logger.info("Gemini client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        return None

def generate_images_from_prompts(prompts: List[str], output_dir: str) -> Optional[List[str]]:
    """
    Generates images from a list of prompts using Google Gemini 2.0 Flash.
    
    Args:
        prompts: List of text prompts for image generation
        output_dir: Directory to save generated images
        
    Returns:
        List of paths to generated images, or None if generation fails
    """
    client = initialize_gemini_client()
    if not client:
        logger.error("Failed to initialize Gemini client")
        return None
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Initialize cost tracker
    cost_tracker = CostTracker()
    
    try:
        logger.info("Starting image generation with Gemini 2.0 Flash")
        
        generated_paths = []
        
        for i, prompt in enumerate(prompts):
            try:
                logger.info(f"Generating image {i+1}/{len(prompts)} for prompt: '{prompt[:50]}...'")
                
                # Generate image path
                image_path = os.path.join(output_dir, f"image_{i+1:03d}.png")
                
                # Generate image using Gemini
                result = client.generate_image(
                    prompt=prompt,
                    output_path=image_path,
                    include_text_response=False
                )
                
                if result and result.get('saved_path'):
                    generated_paths.append(result['saved_path'])
                    logger.info(f"Image saved: {result['saved_path']}")
                    
                    # Track cost (estimated - Gemini is generally cheaper than Vertex AI)
                    cost_tracker.add_cost("gemini_image_generation", 0.01)  # Approximate cost per image
                else:
                    logger.warning(f"No image generated for prompt {i+1}")
                    
            except Exception as e:
                logger.error(f"Error generating image {i+1}: {e}")
                continue
        
        if generated_paths:
            logger.info(f"Successfully generated {len(generated_paths)} images")
            cost_tracker.save_report()
            return generated_paths
        else:
            logger.error("No images were generated successfully")
            return None
            
    except Exception as e:
        logger.error(f"Error during image generation process: {e}")
        return None

def test_image_generation():
    """Test function to verify image generation works."""
    if not os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") == "your_project_id_here":
        print("Error: GOOGLE_CLOUD_PROJECT environment variable not set.")
        print("Please set your Google Cloud project ID in the .env file.")
        return
    
    print("Testing Google Imagen image generation...")
    
    test_prompts = [
        "A futuristic cyberpunk cityscape at night with neon lights",
        "A serene mountain landscape with a crystal clear lake"
    ]
    
    test_output_dir = "test_images"
    
    try:
        paths = generate_images_from_prompts(test_prompts, test_output_dir)
        if paths:
            print("\nGenerated image paths:")
            for path in paths:
                print(f"  - {path}")
            print("\n✅ Image generation test completed successfully!")
        else:
            print("❌ Image generation test failed.")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_image_generation()
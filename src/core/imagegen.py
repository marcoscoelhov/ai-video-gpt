"""Generates images from prompts using Google Imagen 3 via Vertex AI with Gemini fallback."""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cost_tracker import CostTracker
from config.vertex_ai_client import VertexAIImagenClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_imagen_client():
    """Initialize Vertex AI Imagen client with fallback to Gemini."""
    try:
        client = VertexAIImagenClient(use_vertex_ai_primary=True)
        model_info = client.get_model_info()
        primary_model = model_info['primary_model']
        logger.info(f"Imagen client initialized successfully - Primary: {primary_model}")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Imagen client: {e}")
        return None

def generate_images_from_prompts(prompts: List[str], output_dir: str) -> Optional[List[str]]:
    """
    Generates images from a list of prompts using Google Imagen 3 via Vertex AI with Gemini fallback.
    
    Args:
        prompts: List of text prompts for image generation
        output_dir: Directory to save generated images
        
    Returns:
        List of paths to generated images, or None if generation fails
    """
    client = initialize_imagen_client()
    if not client:
        logger.error("Failed to initialize Imagen client")
        return None
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    print(f"[DEBUG] Geração de imagens - Diretório de saída: {output_dir}")
    print(f"[DEBUG] Geração de imagens - Diretório absoluto: {os.path.abspath(output_dir)}")
    
    # Initialize cost tracker
    cost_tracker = CostTracker()
    
    try:
        model_info = client.get_model_info()
        primary_model = model_info['primary_model']
        logger.info(f"Starting image generation with {primary_model} (Vertex AI: {model_info['vertex_ai_available']}, Gemini: {model_info['gemini_available']})")
        
        generated_paths = []
        
        for i, prompt in enumerate(prompts):
            try:
                logger.info(f"Generating image {i+1}/{len(prompts)} for prompt: '{prompt[:50]}...'")
                
                # Generate image path
                image_path = os.path.join(output_dir, f"image_{i+1:03d}.png")
                print(f"[DEBUG] Salvando imagem: {image_path}")
                print(f"[DEBUG] Caminho absoluto: {os.path.abspath(image_path)}")
                
                # Generate image using Vertex AI or Gemini
                result = client.generate_image(
                    prompt=prompt,
                    output_path=image_path
                )
                
                if result and result.get('success') and result.get('saved_path'):
                    generated_paths.append(result['saved_path'])
                    model_used = result.get('model_used', 'unknown')
                    logger.info(f"Image saved: {result['saved_path']} (Model: {model_used})")
                    
                    # Track cost based on model used
                    if model_used == 'vertex_ai':
                        cost_tracker.add_cost("vertex_ai_image_generation", 0.02)  # Vertex AI cost
                    else:
                        cost_tracker.add_cost("gemini_image_generation", 0.01)  # Gemini cost
                else:
                    error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
                    logger.warning(f"No image generated for prompt {i+1}: {error_msg}")
                    
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
    """Test function to verify image generation works with Vertex AI and Gemini fallback."""
    print("Testing Imagen 3 (Vertex AI) with Gemini fallback...")
    
    # Check if at least one service is configured
    has_vertex_ai = os.getenv("GOOGLE_CLOUD_PROJECT") and os.getenv("GOOGLE_CLOUD_PROJECT") != "your_project_id_here"
    has_gemini = os.getenv("GEMINI_API_KEY")
    
    if not has_vertex_ai and not has_gemini:
        print("Error: Neither GOOGLE_CLOUD_PROJECT nor GEMINI_API_KEY are configured.")
        print("Please set at least one in the .env file.")
        return
    
    if has_vertex_ai:
        print(f"✅ Vertex AI configured - Project: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
    if has_gemini:
        print("✅ Gemini API configured")
    
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
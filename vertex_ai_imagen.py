"""Simplified interface for Google Vertex AI Imagen.

This module provides a simplified, user-friendly interface for generating images
using Google's Vertex AI Imagen models. It wraps the official Vertex AI SDK
to provide an easier-to-use API.
"""

import os
import asyncio
import logging
from typing import Optional, List, Union
from pathlib import Path

try:
    import vertexai
    from vertexai.vision_models import ImageGenerationModel
except ImportError:
    raise ImportError(
        "Required dependencies not found. Please install with: "
        "pip install google-cloud-aiplatform vertexai"
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageResponse:
    """Represents a generated image response."""
    
    def __init__(self, image_data, image_object=None):
        self.image_data = image_data
        self.image_object = image_object
    
    def save(self, filename: str) -> None:
        """Save the generated image to a file.
        
        Args:
            filename: Path where to save the image
        """
        try:
            # Create directory if it doesn't exist
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            
            if self.image_object:
                # Use Vertex AI image object save method
                self.image_object.save(location=filename)
            else:
                # Fallback: save raw image data
                with open(filename, 'wb') as f:
                    f.write(self.image_data)
            
            logger.info(f"Image saved to: {filename}")
        except Exception as e:
            logger.error(f"Failed to save image to {filename}: {e}")
            raise


class ImagenClient:
    """Simplified client for Google Vertex AI Imagen.
    
    This class provides an easy-to-use interface for generating images
    using Google's Imagen models via Vertex AI.
    """
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        """Initialize the Imagen client.
        
        Args:
            project_id: Google Cloud project ID
            location: Google Cloud region (default: us-central1)
        """
        self.project_id = project_id
        self.location = location
        self._initialized = False
        self._model = None
    
    def setup_credentials_from_env(self) -> None:
        """Setup credentials from environment variables.
        
        This method uses Application Default Credentials (ADC).
        Make sure you've run: gcloud auth application-default login
        """
        try:
            # Initialize Vertex AI
            vertexai.init(project=self.project_id, location=self.location)
            self._initialized = True
            logger.info(f"Credentials setup from environment for project: {self.project_id}")
        except Exception as e:
            logger.error(f"Failed to setup credentials from environment: {e}")
            raise
    
    def setup_credentials(self, key_file: str) -> None:
        """Setup credentials from a service account key file.
        
        Args:
            key_file: Path to the service account JSON key file
        """
        try:
            # Set environment variable for service account
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_file
            
            # Initialize Vertex AI
            vertexai.init(project=self.project_id, location=self.location)
            self._initialized = True
            logger.info(f"Credentials setup from key file: {key_file}")
        except Exception as e:
            logger.error(f"Failed to setup credentials from key file {key_file}: {e}")
            raise
    
    def _ensure_initialized(self) -> None:
        """Ensure the client is properly initialized."""
        if not self._initialized:
            # Try to initialize with environment credentials
            self.setup_credentials_from_env()
    
    def _get_model(self, model_name: str) -> ImageGenerationModel:
        """Get or create the image generation model.
        
        Args:
            model_name: Name of the Imagen model to use
            
        Returns:
            ImageGenerationModel instance
        """
        try:
            # Map user-friendly model names to actual model IDs
            model_mapping = {
                "imagen-4.0-fast-generate-preview-06-06": "imagen-3.0-generate-002",
                "imagen-4.0": "imagen-3.0-generate-002",
                "imagen-3.0": "imagen-3.0-generate-002",
                "imagen-3.0-generate-002": "imagen-3.0-generate-002"
            }
            
            actual_model = model_mapping.get(model_name, model_name)
            return ImageGenerationModel.from_pretrained(actual_model)
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise
    
    async def generate(
        self,
        prompt: str,
        model: str = "imagen-3.0-generate-002",
        aspect_ratio: str = "1:1",
        count: int = 1
    ) -> ImageResponse:
        """Generate an image from a text prompt.
        
        Args:
            prompt: Text description of the image to generate
            model: Model name to use for generation
            aspect_ratio: Aspect ratio of the generated image (e.g., "1:1", "16:9")
            count: Number of images to generate (currently only 1 is supported)
            
        Returns:
            ImageResponse object with the generated image
        """
        self._ensure_initialized()
        
        if count != 1:
            logger.warning("Only count=1 is currently supported. Using count=1.")
        
        try:
            # Get the model
            model_instance = self._get_model(model)
            
            # Run the generation in a thread pool to make it async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model_instance.generate_images(
                    prompt=prompt,
                    number_of_images=1,
                    aspect_ratio=aspect_ratio,
                    safety_filter_level="block_some",
                    person_generation="allow_adult"
                )
            )
            
            if response.images:
                image = response.images[0]
                return ImageResponse(image_data=None, image_object=image)
            else:
                raise RuntimeError("No image was generated")
                
        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            raise
    
    def generate_sync(
        self,
        prompt: str,
        model: str = "imagen-3.0-generate-002",
        aspect_ratio: str = "1:1",
        count: int = 1
    ) -> ImageResponse:
        """Synchronous version of generate method.
        
        Args:
            prompt: Text description of the image to generate
            model: Model name to use for generation
            aspect_ratio: Aspect ratio of the generated image
            count: Number of images to generate (currently only 1 is supported)
            
        Returns:
            ImageResponse object with the generated image
        """
        # Run the async method in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.generate(prompt, model, aspect_ratio, count)
        )


# Convenience function for quick usage
def generate_image(
    prompt: str,
    project_id: str,
    model: str = "imagen-3.0-generate-002",
    aspect_ratio: str = "1:1",
    output_file: Optional[str] = None
) -> ImageResponse:
    """Quick function to generate a single image.
    
    Args:
        prompt: Text description of the image
        project_id: Google Cloud project ID
        model: Model name to use
        aspect_ratio: Aspect ratio of the image
        output_file: Optional file path to save the image
        
    Returns:
        ImageResponse object
    """
    client = ImagenClient(project_id)
    client.setup_credentials_from_env()
    
    response = client.generate_sync(prompt, model, aspect_ratio)
    
    if output_file:
        response.save(output_file)
    
    return response
"""Example usage of vertex_ai_imagen - User's exact code.

This file demonstrates the exact usage pattern requested by the user.
"""

import asyncio
from vertex_ai_imagen import ImagenClient


async def main():
    """User's exact example code."""
    
    # User's exact code:
    client = ImagenClient(project_id="gen-lang-client-0003871542")
    client.setup_credentials_from_env()  # ou .setup_credentials("key.json")
    
    image = await client.generate(
        prompt="Uma paisagem futurista com céu roxo",
        model="imagen-4.0-fast-generate-preview-06-06",
        aspect_ratio="16:9",
        count=1
    )
    image.save("saida.png")
    
    print("✅ Image generated and saved as 'saida.png'")


if __name__ == "__main__":
    # Run the async function
    asyncio.run(main())
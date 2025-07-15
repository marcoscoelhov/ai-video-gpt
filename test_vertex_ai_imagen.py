"""Test script for the vertex_ai_imagen module.

This script demonstrates how to use the simplified ImagenClient interface
to generate images using Google Vertex AI Imagen.
"""

import asyncio
import os
from vertex_ai_imagen import ImagenClient


async def test_async_generation():
    """Test asynchronous image generation - exactly as user requested."""
    print("🧪 Testing async image generation...")
    
    try:
        # Create client with project ID from environment
        client = ImagenClient(project_id="gen-lang-client-0003871542")
        client.setup_credentials_from_env()  # ou .setup_credentials("key.json")
        
        # Generate image exactly as user's example
        image = await client.generate(
            prompt="Uma paisagem futurista com céu roxo",
            model="imagen-4.0-fast-generate-preview-06-06",
            aspect_ratio="16:9",
            count=1
        )
        
        # Save image
        image.save("saida.png")
        
        print("✅ Async generation successful! Image saved as 'saida.png'")
        
    except Exception as e:
        print(f"❌ Async generation failed: {e}")


def test_sync_generation():
    """Test synchronous image generation."""
    print("\n🧪 Testing sync image generation...")
    
    try:
        # Create client
        client = ImagenClient(project_id="gen-lang-client-0003871542")
        client.setup_credentials_from_env()
        
        # Generate image synchronously
        image = client.generate_sync(
            prompt="Um robô amigável em um jardim colorido",
            model="imagen-3.0-generate-002",
            aspect_ratio="1:1",
            count=1
        )
        
        # Save image
        image.save("test_sync.png")
        
        print("✅ Sync generation successful! Image saved as 'test_sync.png'")
        
    except Exception as e:
        print(f"❌ Sync generation failed: {e}")


def test_different_aspect_ratios():
    """Test different aspect ratios."""
    print("\n🧪 Testing different aspect ratios...")
    
    aspect_ratios = ["1:1", "16:9", "9:16", "4:3"]
    
    for i, ratio in enumerate(aspect_ratios):
        try:
            client = ImagenClient(project_id="gen-lang-client-0003871542")
            client.setup_credentials_from_env()
            
            image = client.generate_sync(
                prompt=f"Uma cidade moderna vista do alto, estilo {ratio}",
                aspect_ratio=ratio,
                count=1
            )
            
            filename = f"test_ratio_{ratio.replace(':', 'x')}.png"
            image.save(filename)
            
            print(f"✅ Generated image with aspect ratio {ratio}: {filename}")
            
        except Exception as e:
            print(f"❌ Failed to generate image with ratio {ratio}: {e}")


def test_credentials_setup():
    """Test different credential setup methods."""
    print("\n🧪 Testing credential setup...")
    
    try:
        client = ImagenClient(project_id="gen-lang-client-0003871542")
        
        # Test environment credentials
        print("Testing setup_credentials_from_env()...")
        client.setup_credentials_from_env()
        print("✅ Environment credentials setup successful")
        
        # Test key file credentials (if file exists)
        key_file = "service-account-key.json"
        if os.path.exists(key_file):
            print(f"Testing setup_credentials('{key_file}')...")
            client.setup_credentials(key_file)
            print("✅ Key file credentials setup successful")
        else:
            print(f"⚠️  Key file '{key_file}' not found, skipping key file test")
            
    except Exception as e:
        print(f"❌ Credential setup failed: {e}")


def main():
    """Run all tests."""
    print("🚀 Starting vertex_ai_imagen tests...")
    print(f"Project ID: gen-lang-client-0003871542")
    print("=" * 50)
    
    # Test credential setup
    test_credentials_setup()
    
    # Test async generation (user's exact example)
    asyncio.run(test_async_generation())
    
    # Test sync generation
    test_sync_generation()
    
    # Test different aspect ratios
    test_different_aspect_ratios()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print("\nGenerated files:")
    print("- saida.png (from async test)")
    print("- test_sync.png (from sync test)")
    print("- test_ratio_*.png (from aspect ratio tests)")


if __name__ == "__main__":
    main()
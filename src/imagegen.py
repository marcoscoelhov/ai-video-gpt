"""Generates images from prompts using the asynchronous Kie.ai API."""
import os
import requests
from PIL import Image
import io
import time

def get_generation_status(task_id, api_key):
    """Gets the status of an image generation task."""
    status_url = f"https://api.kie.ai/api/v1/gpt4o-image/record-info?taskId={task_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(status_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"     - Error checking status: {e}")
        return None

def generate_images_from_prompts(prompts, output_dir):
    """
    Generates images from a list of prompts using the asynchronous Kie.ai API.
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("Error: KIE_API_KEY environment variable not set.")
        return []

    image_paths = []
    generate_url = "https://api.kie.ai/api/v1/gpt4o-image/generate"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for i, prompt in enumerate(prompts):
        print(f"  -> Submitting image generation for prompt {i+1}/{len(prompts)}: '{prompt[:40]}...' ")
        
        payload = {
            "prompt": prompt,
            "model": "4o-image",
            "size": "1:1",
            "response_format": "url"
        }

        try:
            # 1. Start generation
            response = requests.post(generate_url, headers=headers, json=payload)
            response.raise_for_status()
            
            initial_data = response.json()
            print(f"     - Initial response: {initial_data}")
            task_id = initial_data.get('data', {}).get('taskId')
            
            if not task_id:
                raise KeyError("'taskId' not found in the initial response.")

            print(f"     - Generation started with taskId: {task_id}")

            # 2. Poll for result
            start_time = time.time()
            timeout = 180 # seconds
            while time.time() - start_time < timeout:
                status_data = get_generation_status(task_id, api_key)
                if status_data:
                    print(f"     - Polling status: {status_data.get('data', {}).get('status')}")
                    task_status = status_data.get('data', {}).get('status')

                    if task_status == 'SUCCESS':
                        response_data = status_data.get('data', {}).get('response', {})
                        image_urls = response_data.get('resultUrls')
                        
                        if not image_urls:
                             raise KeyError("'resultUrls' not found in the final response.")

                        image_url = image_urls[0]
                        print(f"     - Image ready at URL: {image_url}")
                        image_response = requests.get(image_url)
                        image_response.raise_for_status()
                        image_data = image_response.content
                        
                        image_path = os.path.join(output_dir, f"image_{i+1:02d}.png")
                        with open(image_path, "wb") as f:
                            f.write(image_data)
                        
                        image_paths.append(image_path)
                        print(f"     - Image saved to {image_path}")
                        break
                    elif task_status == 'failed':
                        raise Exception(f"Generation failed: {status_data.get('data', {}).get('errorMessage')}")
                
                time.sleep(5)
            else:
                print("     - Polling timed out after 180 seconds.")
                raise TimeoutError("Image generation timed out.")

        except (requests.exceptions.RequestException, KeyError, IndexError, TimeoutError, Exception) as e:
            print(f"     - Error during image generation process: {e}")
            placeholder_path = os.path.join(output_dir, f"image_{i+1:02d}_placeholder.png")
            img = Image.new('RGB', (1024, 1024), color = 'blue')
            img.save(placeholder_path)
            image_paths.append(placeholder_path)
            print(f"     - Saved blue placeholder image to {placeholder_path}")

    return image_paths

if __name__ == '__main__':
    if not os.getenv("KIE_API_KEY"):
        print("Error: KIE_API_KEY environment variable not set.")
    else:
        test_prompts = [
            "digital comic book art of a lone astronaut on a red planet, looking at a blue sunset.",
            "digital comic book art of a futuristic spaceship landing softly in a crater."
        ]
        # For testing, create a dummy output directory
        test_output_dir = "test_output_images"
        os.makedirs(test_output_dir, exist_ok=True)
        paths = generate_images_from_prompts(test_prompts, test_output_dir)
        print("\nGenerated image paths:")
        print(paths)

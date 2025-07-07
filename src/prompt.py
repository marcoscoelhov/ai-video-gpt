"""Extracts image prompts from a structured script."""

def scene_prompts(script_data):
    """
    Extracts visual descriptions from each scene in the structured script.

    Args:
        script_data: A dictionary representing the structured script.

    Returns:
        A list of image prompts.
    """
    if not isinstance(script_data, dict) or "scenes" not in script_data:
        print("Error: Invalid script format. Expected a dictionary with a 'scenes' key.")
        return []

    prompts = []
    for scene in script_data["scenes"]:
        if "visual_description" in scene:
            prompts.append(scene["visual_description"])
        else:
            print(f"Warning: Scene {scene.get('scene', '?')} is missing a 'visual_description'.")

    return prompts

if __name__ == '__main__':
    # Example usage for testing
    test_script = {
      "theme": "The secret life of garden gnomes",
      "title": "Gnome Sweet Gnome",
      "scenes": [
        {
          "scene": 1,
          "visual_description": "digital comic book art of a garden gnome secretly polishing his fishing rod at midnight, with the moon shining brightly.",
          "narration": "At night, the garden reveals its secrets."
        },
        {
          "scene": 2,
          "visual_description": "digital comic book art of two gnomes playing a high-stakes game of poker on a toadstool table.",
          "narration": "Bernard was all in, but Gerald held the winning hand."
        }
      ]
    }
    
    generated_prompts = scene_prompts(test_script)
    print("--- Extracted Prompts ---")
    for i, p in enumerate(generated_prompts):
        print(f"Scene {i+1}: {p}")
    print("-------------------------")
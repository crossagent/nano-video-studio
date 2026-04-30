import sys
import os
# Add the scripts directory to sys.path
sys.path.append(r"d:\nano-video-studio\skills\00-common-tools\scripts")

import nano_video_mcp

def test_validation():
    print("Testing Video validation (missing duration)...")
    res = nano_video_mcp.submit_video_task(
        channel_id="volcengine",
        model_id="doubao-seedance-2-0-fast-260128",
        project="test",
        stage="test",
        prompt="test",
        extra_params={"aspect_ratio": "16:9"}
    )
    print(res)
    
    print("\nTesting Image validation (correct)...")
    # Note: This might actually try to write to DB if valid, so we use a non-existent table if we want to avoid side effects
    # But for a quick test, let's see if it passes validation
    res = nano_video_mcp.submit_image_task(
        channel_id="openrouter",
        model_id="openai/gpt-5.4-image-2",
        project="test",
        stage="test",
        prompt="test",
        extra_params={"size": "1024x1024", "aspect_ratio": "16:9"}
    )
    print(res)

if __name__ == "__main__":
    test_validation()

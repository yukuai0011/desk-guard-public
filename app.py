#!/usr/bin/env python3
"""
GLM-4V Multiple Image Upload Test

This program tests uploading multiple images to the GLM-4V model using the official zhipuai SDK.
It prompts the user for their API key and processes two test images.
"""

import base64
import os
from pathlib import Path
from typing import Dict, List, Any

try:
    from zhipuai import ZhipuAI
except ImportError:
    print("Error: zhipuai package not found. Please install it using: pip install zhipuai")
    exit(1)


def encode_image(image_path: str) -> str | None:
    """
    Encode an image file to base64 string.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded string of the image, or None if failed
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None


def test_security_monitoring():
    """
    Test computer security monitoring using two images:
    - First image: authorized owner (reference)
    - Second image: current person near computer (monitoring)
    """
    # Prompt user for API key
    api_key = input("Please enter your GLM-4V API key: ").strip()
    if not api_key:
        print("Error: API key is required")
        return
    
    # Initialize the client
    try:
        client = ZhipuAI(api_key=api_key)
        print("✓ GLM-4V client initialized successfully")
    except Exception as e:
        print(f"Error initializing client: {e}")
        return
    
    # Test image paths
    image_paths = [
        r"image1",
        r"image2"
    ]
    
    # Check if images exist
    existing_images = []
    for image_path in image_paths:
        if os.path.exists(image_path):
            existing_images.append(image_path)
            print(f"✓ Found image: {Path(image_path).name}")
        else:
            print(f"✗ Image not found: {image_path}")
    
    if not existing_images:
        print("Error: No images found for security monitoring. Please ensure both owner and monitoring images exist.")
        return
    
    if len(existing_images) < 2:
        print("Warning: Only one image found. Security monitoring requires both owner and current user images.")
        print("Proceeding with available image(s)...")
    
    print(f"\nProcessing {len(existing_images)} image(s) for security analysis...")
    
    # Encode images to base64
    encoded_images = []
    for i, image_path in enumerate(existing_images):
        image_type = "Owner (reference)" if i == 0 else "Current user (monitoring)"
        print(f"Encoding {image_type}: {Path(image_path).name}...")
        encoded_image = encode_image(image_path)
        if encoded_image:
            encoded_images.append({
                "path": image_path,
                "name": Path(image_path).name,
                "base64": encoded_image,
                "type": image_type
            })
            print(f"✓ Successfully encoded {image_type}: {Path(image_path).name}")
        else:
            print(f"✗ Failed to encode {image_type}: {Path(image_path).name}")
    
    if not encoded_images:
        print("Error: No images could be encoded for security monitoring")
        return
    
    # Prepare message content with multiple images for security monitoring
    message_content = [
        {
            "type": "text",
            "text": f"""You are a computer security monitoring system. I have uploaded 2 images:

1. FIRST IMAGE: This is the authorized owner of the computer (reference image)
2. SECOND IMAGE: This is the current person near the computer (monitoring image)

Your task:
- Compare the person in the second image with the owner in the first image
- Identify them by BOTH facial features AND clothing/appearance
- Determine if the person in the second image is the same as the owner OR a different person

SECURITY ALERT CONDITIONS:
- If the person in the second image is NOT the owner (different face or different clothing)
- AND they are approaching the computer too closely by either:
  * Having their hand reaching toward the computer/keyboard/mouse
  * Putting their face very close to the screen (closer than normal viewing distance)

RESPONSE FORMAT:
You must provide a threat possibility rate and analysis in this exact format:

THREAT LEVEL: [0-100]%
[Analysis result below]

If threat detected (70-100%): "🚨 SECURITY ALERT: Unauthorized person detected approaching computer. [Describe what you see and why it's suspicious]"

If moderate concern (30-69%): "⚠️ CAUTION: [Describe the situation and why there might be some concern]"

If all normal (0-29%): "✅ ALL NORMAL: [Briefly describe the situation - either owner at computer or no security threat detected]"

SCORING GUIDELINES:
- 0-29%: Owner present OR unauthorized person at safe distance
- 30-69%: Unauthorized person present but not immediately threatening
- 70-100%: Unauthorized person approaching computer/reaching for it/face too close

Analyze the images now:"""
        }
    ]
    
    # Add each encoded image to the message
    for img_data in encoded_images:
        message_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{img_data['base64']}"
            }
        })
        print(f"✓ Added {img_data['type']}: {img_data['name']} to analysis")
    
    print(f"\n🔍 Analyzing {len(encoded_images)} image(s) for security threats...")
    
    try:
        # Make the API call
        response = client.chat.completions.create(
            model="glm-4v-flash",
            messages=[
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            extra_body={
                "temperature": 0.3,  # Lower temperature for more consistent security analysis
                "max_tokens": 1000
            }
        )
        
        print("✓ Security analysis completed")
        print("\n" + "="*60)
        print("🛡️  SECURITY MONITORING RESULT:")
        print("="*60)
        print(response.choices[0].message.content)
        print("="*60)
        
        # Display usage information if available
        if hasattr(response, 'usage'):
            print(f"\nUsage Information:")
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Completion tokens: {response.usage.completion_tokens}")
            print(f"Total tokens: {response.usage.total_tokens}")
            
    except Exception as e:
        print(f"⚠️  Error during security analysis: {e}")
        print("Please check your API key and network connection.")
        print("Security monitoring temporarily unavailable.")


def test_single_image_upload():
    """
    Test uploading a single image to GLM-4V model.
    """
    # Prompt user for API key
    api_key = input("Please enter your GLM-4V API key: ").strip()
    if not api_key:
        print("Error: API key is required")
        return
    
    # Initialize the client
    try:
        client = ZhipuAI(api_key=api_key)
        print("✓ GLM-4V client initialized successfully")
    except Exception as e:
        print(f"Error initializing client: {e}")
        return
    
    # Test with the first available image
    image_paths = [
        r"C:\Users\yukua\Downloads\WIN_20250622_14_28_40_Pro.jpg",
        r"C:\Users\yukua\Downloads\WIN_20250622_15_21_38_Pro.jpg"
    ]
    
    test_image = None
    for image_path in image_paths:
        if os.path.exists(image_path):
            test_image = image_path
            break
    
    if not test_image:
        print("Error: No test images found")
        return
    
    print(f"Testing with single image: {Path(test_image).name}")
    
    # Encode the image
    encoded_image = encode_image(test_image)
    if not encoded_image:
        print("Error: Failed to encode image")
        return
    
    try:
        # Make the API call with single image
        response = client.chat.completions.create(
            model="glm-4v-flash",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze this image and describe what you see in detail."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            extra_body={
                "temperature": 0.7,
                "max_tokens": 500
            }
        )
        
        print("✓ Successfully received response from GLM-4V")
        print("\n" + "="*60)
        print("GLM-4V RESPONSE (Single Image):")
        print("="*60)
        print(response.choices[0].message.content)
        print("="*60)
        
    except Exception as e:
        print(f"Error calling GLM-4V API: {e}")


def main():
    """
    Main function to run the computer security monitoring system.
    """
    print("🛡️  Computer Security Monitoring System")
    print("=====================================")
    print("This system monitors computer access using GLM-4V vision analysis.")
    print("It compares authorized users with current users to detect unauthorized access.")
    print("Make sure you have a valid API key from https://open.bigmodel.cn/")
    print()
    
    while True:
        print("Choose monitoring mode:")
        print("1. 🔍 Security monitoring (compare owner vs current user)")
        print("2. 📷 Single image analysis")
        print("3. ❌ Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n--- 🛡️  Security Monitoring Mode ---")
            test_security_monitoring()
        elif choice == "2":
            print("\n--- 📷 Single Image Analysis ---")
            test_single_image_upload()
        elif choice == "3":
            print("👋 Goodbye! Stay secure!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
        
        print("\n" + "-"*60 + "\n")


if __name__ == "__main__":
    main()

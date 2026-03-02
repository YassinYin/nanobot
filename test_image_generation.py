#!/usr/bin/env python3
"""Test script for image generation with optional input image."""

import asyncio
import json
from pathlib import Path

from nanobot.agent.tools.image import ImageGenerateTool
from nanobot.config.loader import load_config


async def test_text_to_image():
    """Test: Text only → Image"""
    print("\n" + "="*60)
    print("Test 1: Text to Image")
    print("="*60)

    config = load_config()
    tool = ImageGenerateTool(config)

    result = await tool.execute(
        prompt="Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme",
        model="google/gemini-3.1-flash-image-preview",
    )

    print(f"Result: {result}")
    if result.startswith("Error"):
        print("❌ Failed")
    else:
        data = json.loads(result)
        print(f"✅ Success! Generated {len(data['files'])} image(s)")
        for f in data['files']:
            print(f"   📄 {f}")


async def test_image_to_image():
    """Test: Image + Text → Image"""
    print("\n" + "="*60)
    print("Test 2: Image + Text to Image")
    print("="*60)

    config = load_config()
    tool = ImageGenerateTool(config)

    # You need to provide a real image path here
    input_image = "/Users/yinrongjie/Desktop/nanobot/images/test_input.png"

    if not Path(input_image).exists():
        print(f"⚠️  Skipping test - input image not found: {input_image}")
        print("   Create a test image at this path to run this test")
        return

    result = await tool.execute(
        prompt="Make this image look like it's in a fancy restaurant with a Gemini theme",
        model="google/gemini-3.1-flash-image-preview",
        input_image=input_image,
    )

    print(f"Result: {result}")
    if result.startswith("Error"):
        print("❌ Failed")
    else:
        data = json.loads(result)
        print(f"✅ Success! Generated {len(data['files'])} image(s)")
        for f in data['files']:
            print(f"   📄 {f}")


async def main():
    print("\n🧪 Testing Image Generation Tool")
    print("="*60)

    # Test 1: Text only
    await test_text_to_image()

    # Test 2: Image + Text
    await test_image_to_image()

    print("\n" + "="*60)
    print("✅ Tests completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

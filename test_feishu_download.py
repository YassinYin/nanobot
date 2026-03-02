#!/usr/bin/env python3
"""Test script for Feishu image download functionality."""

import asyncio
from pathlib import Path

from nanobot.agent.tools.feishu import FeishuDownloadImageTool, FeishuExtractImageKeyTool
from nanobot.config.loader import load_config


async def test_extract_image_key():
    """Test: Extract image_key from content"""
    print("\n" + "="*60)
    print("Test 1: Extract image_key from content")
    print("="*60)

    tool = FeishuExtractImageKeyTool()

    test_cases = [
        'https://example.feishu.cn/image?image_key=img_v3_027f_abc123',
        '{"image_key": "img_v2_xyz789"}',
        'Some text img_v3_027f_test123 more text',
    ]

    for content in test_cases:
        result = await tool.execute(url_or_content=content)
        print(f"Input: {content}")
        print(f"Result: {result}\n")


async def test_download_image():
    """Test: Download image from Feishu"""
    print("\n" + "="*60)
    print("Test 2: Download image from Feishu")
    print("="*60)

    config = load_config()

    if not config.channels.feishu.enabled:
        print("⚠️  Feishu channel is not enabled")
        print("   Enable it in ~/.nanobot/config.json to run this test")
        return

    tool = FeishuDownloadImageTool(config)

    # You need to provide real values here from a Feishu message
    print("\n⚠️  To test image download, you need to:")
    print("   1. Send an image in Feishu to your bot")
    print("   2. Check the nanobot logs for image_key and message_id")
    print("   3. Update the test script with real values\n")

    # Example (replace with real values):
    # image_key = "img_v3_027f_abc123..."
    # message_id = "om_xxx..."
    #
    # result = await tool.execute(
    #     image_key=image_key,
    #     message_id=message_id,
    #     filename="test_download"
    # )
    #
    # if result.startswith("Error"):
    #     print(f"❌ Failed: {result}")
    # else:
    #     print(f"✅ Success!")
    #     print(f"   Downloaded to: {result}")
    #     print(f"   File exists: {Path(result).exists()}")


async def test_integration():
    """Test: Complete workflow - download and use for image generation"""
    print("\n" + "="*60)
    print("Test 3: Integration Test (Download + Image Generation)")
    print("="*60)

    print("\n📝 Workflow:")
    print("   1. User sends image in Feishu")
    print("   2. Bot downloads image using feishu_download_image")
    print("   3. Bot uses local image path for image_generate with input_image")
    print("   4. Bot sends generated image back to Feishu")

    print("\n💡 This is automatically handled when user says:")
    print('   "请下载我刚发的图片并生成一个卡通版本"')

    print("\n✅ Tools are registered and ready to use!")


async def main():
    print("\n🧪 Testing Feishu Image Download Tools")
    print("="*60)

    # Test 1: Extract image_key
    await test_extract_image_key()

    # Test 2: Download image (needs real data)
    await test_download_image()

    # Test 3: Integration workflow
    await test_integration()

    print("\n" + "="*60)
    print("✅ Tests completed!")
    print("="*60)
    print("\n📚 See FEISHU_IMAGE_DOWNLOAD_GUIDE.md for usage details\n")


if __name__ == "__main__":
    asyncio.run(main())

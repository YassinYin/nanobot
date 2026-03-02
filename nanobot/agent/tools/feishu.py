"""Feishu-specific tools for downloading images and files."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any, TYPE_CHECKING

from loguru import logger

from nanobot.agent.tools.base import Tool

if TYPE_CHECKING:
    from nanobot.config.schema import Config

try:
    import lark_oapi as lark
    from lark_oapi.api.im.v1 import GetMessageResourceRequest
    FEISHU_AVAILABLE = True
except ImportError:
    FEISHU_AVAILABLE = False
    lark = None


class FeishuDownloadImageTool(Tool):
    """Download images from Feishu/Lark to local storage."""

    def __init__(self, config: "Config"):
        self._config = config
        self._output_dir = Path("/Users/yinrongjie/Desktop/nanobot/receiv_img")
        self._output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def name(self) -> str:
        return "feishu_download_image"

    @property
    def description(self) -> str:
        return (
            "Download an image from Feishu/Lark to local storage. "
            "Requires image_key and message_id from Feishu messages. "
            "Returns the local file path."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "image_key": {
                    "type": "string",
                    "description": "Feishu image key (e.g., img_v2_xxx or img_v3_xxx)"
                },
                "message_id": {
                    "type": "string",
                    "description": "Feishu message ID containing the image"
                },
                "filename": {
                    "type": "string",
                    "description": "Optional: custom filename (without extension)"
                },
            },
            "required": ["image_key", "message_id"],
        }

    async def execute(
        self,
        image_key: str,
        message_id: str,
        filename: str | None = None,
        **kwargs: Any,
    ) -> str:
        if not FEISHU_AVAILABLE:
            return (
                "Error: Feishu SDK not installed. "
                "Install it with `pip install lark-oapi` and restart."
            )

        feishu_config = self._config.channels.feishu
        if not feishu_config.enabled or not feishu_config.app_id or not feishu_config.app_secret:
            return (
                "Error: Feishu channel not configured. "
                "Set channels.feishu.enabled=true and provide appId/appSecret in ~/.nanobot/config.json"
            )

        # Create Feishu client
        client = lark.Client.builder() \
            .app_id(feishu_config.app_id) \
            .app_secret(feishu_config.app_secret) \
            .build()

        # Download image
        try:
            data, original_filename = await self._download_image(
                client, message_id, image_key
            )

            if not data:
                return f"Error: Failed to download image. Check if image_key={image_key} and message_id={message_id} are valid."

            # Determine filename
            if filename:
                # Extract extension from original filename
                ext = Path(original_filename or "image.jpg").suffix
                save_filename = f"{filename}{ext}"
            else:
                save_filename = original_filename or f"{image_key[:16]}.jpg"

            # Save to disk
            file_path = self._output_dir / save_filename
            file_path.write_bytes(data)

            logger.info(f"Downloaded Feishu image to {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"Error downloading Feishu image: {e}")
            return f"Error: Failed to download image: {str(e)}"

    async def _download_image(
        self, client: Any, message_id: str, image_key: str
    ) -> tuple[bytes | None, str | None]:
        """Download image from Feishu using message_id and image_key."""
        loop = asyncio.get_running_loop()

        def _sync_download():
            try:
                request = GetMessageResourceRequest.builder() \
                    .message_id(message_id) \
                    .file_key(image_key) \
                    .type("image") \
                    .build()

                response = client.im.v1.message_resource.get(request)

                if response.success():
                    file_data = response.file
                    # GetMessageResourceRequest returns BytesIO, need to read bytes
                    if hasattr(file_data, 'read'):
                        file_data = file_data.read()

                    filename = getattr(response, 'file_name', None)
                    return file_data, filename
                else:
                    logger.error(
                        f"Failed to download Feishu image: code={response.code}, "
                        f"msg={response.msg}, log_id={response.get_log_id()}"
                    )
                    return None, None

            except Exception as e:
                logger.error(f"Exception downloading Feishu image: {e}")
                return None, None

        return await loop.run_in_executor(None, _sync_download)


class FeishuExtractImageKeyTool(Tool):
    """Extract image_key from Feishu image URL or content."""

    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return "feishu_extract_image_key"

    @property
    def description(self) -> str:
        return (
            "Extract image_key from Feishu image URL or message content. "
            "Useful when you have a Feishu image link but need the image_key for downloading."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url_or_content": {
                    "type": "string",
                    "description": "Feishu image URL or content containing image_key"
                },
            },
            "required": ["url_or_content"],
        }

    async def execute(self, url_or_content: str, **kwargs: Any) -> str:
        """Extract image_key from URL or content."""
        # Pattern for image_key (img_v2_xxx or img_v3_xxx or img_xxx)
        patterns = [
            r'img_v[23]_[a-zA-Z0-9_-]+',
            r'img_[a-zA-Z0-9_-]{20,}',
            r'"image_key"\s*:\s*"([^"]+)"',
        ]

        for pattern in patterns:
            match = re.search(pattern, url_or_content)
            if match:
                image_key = match.group(1) if match.lastindex else match.group(0)
                return f"Found image_key: {image_key}"

        return "Error: No image_key found in the provided content"

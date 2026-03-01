"""Image generation tool."""

from __future__ import annotations

import asyncio
import base64
import imghdr
import io
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import litellm

from nanobot.agent.tools.base import Tool
from nanobot.config.schema import Config
from nanobot.providers.litellm_provider import LiteLLMProvider
from nanobot.utils.helpers import ensure_dir, safe_filename

_DEFAULT_OUTPUT_DIR = Path("/Users/yinrongjie/Desktop/nanobot/images")


class ImageGenerateTool(Tool):
    """Generate images from text prompts using a configured model."""

    def __init__(self, config: Config):
        self._config = config
        self._output_dir = ensure_dir(_DEFAULT_OUTPUT_DIR)

    @property
    def name(self) -> str:
        return "image_generate"

    @property
    def description(self) -> str:
        return (
            "Generate image(s) from a text prompt using the configured image model. "
            "Returns local file paths; to deliver images to the user, call the message tool "
            "with media set to those paths."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Image generation prompt"},
                "model": {"type": "string", "description": "Optional: override image model"},
                "n": {"type": "integer", "minimum": 1, "maximum": 4, "description": "Number of images"},
                "size": {"type": "string", "description": "Image size (e.g., 1024x1024)"},
                "quality": {"type": "string", "description": "Image quality (provider-specific)"},
                "style": {"type": "string", "description": "Image style (provider-specific)"},
                "response_format": {"type": "string", "enum": ["url", "b64_json"]},
                "timeout": {"type": "number", "description": "Request timeout in seconds"},
            },
            "required": ["prompt"],
        }

    async def execute(
        self,
        prompt: str,
        model: str | None = None,
        n: int | None = None,
        size: str | None = None,
        quality: str | None = None,
        style: str | None = None,
        response_format: str | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> str:
        image_model = model or self._config.agents.defaults.image_model
        if not image_model:
            return (
                "Error: Image model not configured. Set agents.defaults.imageModel in ~/.nanobot/config.json "
                "or pass model in the tool call."
            )

        provider_cfg = self._config.get_provider(image_model)
        provider_name = self._config.get_provider_name(image_model)

        # Prefer Zenmux for Google/Gemini image models when configured.
        if image_model.startswith("google/") and getattr(self._config.providers, "zenmux", None):
            zen = self._config.providers.zenmux
            if zen.api_key:
                provider_cfg = zen
                provider_name = "zenmux"

        api_key = provider_cfg.api_key if provider_cfg else None
        api_base = (provider_cfg.api_base if provider_cfg else None) or self._config.get_api_base(image_model)
        image_api_base = provider_cfg.image_api_base if provider_cfg else None
        extra_headers = provider_cfg.extra_headers if provider_cfg else None

        if not api_key and not api_base and not extra_headers:
            return (
                f"Error: No API key or API base configured for image model '{image_model}'. "
                "Set it under providers in ~/.nanobot/config.json."
            )

        if _use_google_genai(image_model, api_base, provider_name):
            return await _generate_with_google_genai(
                model=image_model,
                prompt=prompt,
                api_key=api_key,
                api_base=image_api_base or api_base or "https://zenmux.ai/api/vertex-ai",
                output_dir=self._output_dir,
            )

        # Ensure LiteLLM environment is prepared for this provider/model.
        prev_api_base = getattr(litellm, "api_base", None)
        resolver = LiteLLMProvider(
            api_key=api_key,
            api_base=api_base,
            default_model=image_model,
            extra_headers=extra_headers,
            provider_name=provider_name,
        )
        resolved_model = resolver._resolve_model(image_model)
        litellm.api_base = prev_api_base

        params: dict[str, Any] = {
            "prompt": prompt,
            "model": resolved_model,
            "n": max(1, min(n or 1, 4)),
        }
        if size:
            params["size"] = size
        if quality:
            params["quality"] = quality
        if style:
            params["style"] = style
        if response_format:
            params["response_format"] = response_format
        if timeout:
            params["timeout"] = timeout
        if api_key:
            params["api_key"] = api_key
        if api_base:
            params["api_base"] = api_base
        if extra_headers:
            params["extra_headers"] = extra_headers

        try:
            response = await litellm.aimage_generation(**params)
        except Exception as e:
            return f"Error: Image generation failed: {str(e)}"

        files: list[str] = []
        revised_prompts: list[str] = []

        data_items = getattr(response, "data", None) or []
        output_format = getattr(response, "output_format", None)
        for idx, item in enumerate(data_items):
            b64_json = _get_field(item, "b64_json")
            url = _get_field(item, "url")
            revised = _get_field(item, "revised_prompt")
            if revised:
                revised_prompts.append(revised)
            try:
                if b64_json:
                    raw = base64.b64decode(b64_json)
                    files.append(str(self._write_image(raw, prompt, idx, output_format)))
                elif url:
                    raw = await _download_image(url)
                    if raw:
                        files.append(str(self._write_image(raw, prompt, idx, output_format)))
            except Exception:
                continue

        if not files:
            return "Error: Image generation returned no image data."

        return json.dumps(
            {
                "model": image_model,
                "resolved_model": resolved_model,
                "files": files,
                "revised_prompts": revised_prompts or None,
            },
            ensure_ascii=False,
        )

    def _write_image(self, data: bytes, prompt: str, idx: int, output_format: str | None) -> Path:
        slug = safe_filename(prompt[:50]) or "image"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = _detect_extension(data, output_format)
        filename = f"{slug}_{timestamp}_{idx}{ext}"
        path = self._output_dir / filename
        path.write_bytes(data)
        return path


def _get_field(item: Any, key: str) -> Any:
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


def _detect_extension(data: bytes, output_format: str | None) -> str:
    if output_format:
        ext = output_format.lower().lstrip(".")
        if ext == "jpeg":
            ext = "jpg"
        return f".{ext}"
    kind = imghdr.what(None, h=data)
    if kind == "jpeg":
        kind = "jpg"
    return f".{kind}" if kind else ".png"


async def _download_image(url: str) -> bytes | None:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content
    except Exception:
        return None


def _use_google_genai(model: str, api_base: str | None, provider_name: str | None) -> bool:
    if model.startswith("google/"):
        return True
    if provider_name == "zenmux" and api_base and "vertex-ai" in api_base:
        return True
    return False


async def _generate_with_google_genai(
    model: str,
    prompt: str,
    api_key: str | None,
    api_base: str,
    output_dir: Path,
) -> str:
    if not api_key:
        return "Error: Missing API key for Google GenAI image generation."

    try:
        from google import genai
        from google.genai import types
    except Exception:
        return (
            "Error: google-genai is not installed. "
            "Install it with `pip install google-genai` and restart the gateway."
        )

    def _call():
        client = genai.Client(
            api_key=api_key,
            vertexai=True,
            http_options=types.HttpOptions(api_version="v1", base_url=api_base),
        )
        return client.models.generate_content(
            model=model,
            contents=[prompt],
            config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
        )

    try:
        response = await asyncio.to_thread(_call)
    except Exception as e:
        return f"Error: Image generation failed: {str(e)}"

    files: list[str] = []
    revised_prompts: list[str] = []
    for idx, part in enumerate(getattr(response, "parts", []) or []):
        text = getattr(part, "text", None)
        if text:
            revised_prompts.append(text)
        inline = getattr(part, "inline_data", None)
        if inline is None:
            continue
        data = getattr(inline, "data", None)
        raw: bytes | None = None
        if isinstance(data, bytes):
            raw = data
        elif isinstance(data, str):
            try:
                raw = base64.b64decode(data)
            except Exception:
                raw = None
        if raw is None and hasattr(part, "as_image"):
            try:
                img = part.as_image()
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                raw = buf.getvalue()
            except Exception:
                raw = None
        if raw:
            slug = safe_filename(prompt[:50]) or "image"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{slug}_{timestamp}_{idx}.png"
            path = output_dir / filename
            path.write_bytes(raw)
            files.append(str(path))

    if not files:
        return "Error: Image generation returned no image data."

    return json.dumps(
        {
            "model": model,
            "resolved_model": model,
            "files": files,
            "revised_prompts": revised_prompts or None,
        },
        ensure_ascii=False,
    )

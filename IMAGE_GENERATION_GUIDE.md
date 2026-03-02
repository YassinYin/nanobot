# 图片生成功能使用指南

## 🎨 功能说明

现在 nanobot 支持两种图片生成模式：

1. **文本生成图片**（Text-to-Image）：仅使用文本提示生成图片
2. **图片+文本生成图片**（Image-to-Image）：基于输入图片和文本提示生成新图片

## 📋 配置要求

### 1. 安装依赖

确保 `google-genai` 已安装：
```bash
uv sync
uv tool install --editable . --force
```

### 2. 配置 API

在 `~/.nanobot/config.json` 中配置：

```json
{
  "agents": {
    "defaults": {
      "imageModel": "google/gemini-3.1-flash-image-preview"
    }
  },
  "providers": {
    "zenmux": {
      "apiKey": "YOUR_ZENMUX_API_KEY",
      "apiBase": "https://zenmux.ai/api/v1",
      "imageApiBase": "https://zenmux.ai/api/vertex-ai"
    }
  }
}
```

## 🚀 使用方法

### 方式 1: 通过聊天直接使用

启动 gateway 后，直接在聊天中请求：

**文本生成图片：**
```
请帮我生成一张图片：一个在高档餐厅里的纳米香蕉料理，带有 Gemini 主题
```

**图片+文本生成图片：**
```
请基于 /path/to/input.png 这张图片，生成一个高档餐厅版本，加上 Gemini 主题
```

### 方式 2: 通过 Python 代码调用

```python
import asyncio
import json
from nanobot.agent.tools.image import ImageGenerateTool
from nanobot.config.loader import load_config

async def generate_image():
    config = load_config()
    tool = ImageGenerateTool(config)

    # 方式 1: 仅文本
    result = await tool.execute(
        prompt="Create a picture of a nano banana dish",
        model="google/gemini-3.1-flash-image-preview"
    )

    # 方式 2: 图片 + 文本
    result = await tool.execute(
        prompt="Make this image look like it's in a fancy restaurant",
        model="google/gemini-3.1-flash-image-preview",
        input_image="/path/to/input.png"
    )

    data = json.loads(result)
    print(f"Generated images: {data['files']}")

asyncio.run(generate_image())
```

### 方式 3: 直接调用 Google GenAI

```python
from google import genai
from google.genai import types

client = genai.Client(
    api_key="YOUR_API_KEY",
    vertexai=True,
    http_options=types.HttpOptions(
        api_version='v1',
        base_url='https://zenmux.ai/api/vertex-ai'
    )
)

# 仅文本生成
response = client.models.generate_content(
    model="google/gemini-3.1-flash-image-preview",
    contents=["Create a picture of a nano banana dish"],
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"]
    )
)

# 图片+文本生成
from pathlib import Path
image_data = Path("input.png").read_bytes()

response = client.models.generate_content(
    model="google/gemini-3.1-flash-image-preview",
    contents=[
        types.Part.from_bytes(data=image_data, mime_type="image/png"),
        "Make this look like a fancy restaurant dish"
    ],
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"]
    )
)

# 保存结果
for part in response.parts:
    if part.text:
        print(part.text)
    elif part.inline_data:
        image = part.as_image()
        image.save("output.png")
```

## 🧪 运行测试

```bash
cd /Users/yinrongjie/Documents/code/nanobot
python test_image_generation.py
```

## 📝 工具参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `prompt` | string | ✅ | 图片生成提示词 |
| `model` | string | ❌ | 覆盖默认模型（默认使用配置中的 imageModel） |
| `input_image` | string | ❌ | **新增**：输入图片路径，用于 image-to-image |
| `n` | integer | ❌ | 生成图片数量（1-4） |
| `size` | string | ❌ | 图片尺寸（如 "1024x1024"） |
| `quality` | string | ❌ | 图片质量（提供商特定） |
| `style` | string | ❌ | 图片风格（提供商特定） |

## 📤 返回格式

工具返回 JSON 字符串：

```json
{
  "model": "google/gemini-3.1-flash-image-preview",
  "resolved_model": "google/gemini-3.1-flash-image-preview",
  "files": [
    "/Users/yinrongjie/Desktop/nanobot/images/nano_banana_20260301_170000_0.png"
  ],
  "revised_prompts": ["生成的图片说明..."]
}
```

生成的图片默认保存在：`~/Desktop/nanobot/images/`

## 🔍 支持的图片格式

输入图片支持：
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- WebP (.webp)

## ⚠️ 注意事项

1. **模型支持**：图片+文本生成功能目前仅支持 Google Gemini 模型（以 `google/` 开头的模型）
2. **图片路径**：输入图片路径支持绝对路径和相对路径（相对于工作目录）
3. **文件大小**：注意输入图片的文件大小限制（建议 < 10MB）
4. **API 限制**：注意 API 调用频率限制和配额

## 🐛 故障排除

**错误：`Input image not found`**
- 检查图片路径是否正确
- 确保文件存在且有读取权限

**错误：`google-genai is not installed`**
```bash
uv sync
uv tool install --editable . --force
```

**错误：`Missing API key`**
- 检查 `~/.nanobot/config.json` 中的 API key 配置
- 确保配置了 `zenmux` 或相应的提供商

## 📚 参考资料

- [Google GenAI 文档](https://ai.google.dev/api/python)
- [Zenmux API 文档](https://zenmux.ai/docs)

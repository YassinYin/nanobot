# 🎉 飞书图片自动下载功能

## ✨ 好消息！

**飞书图片已经在自动下载了！** 你不需要做任何额外配置。

## 🔄 工作原理

当你在飞书向机器人发送图片时，系统会**自动**完成以下操作：

### 1. 自动下载图片

```
用户 → 飞书发送图片
     ↓
飞书 Channel 接收消息
     ↓
自动下载到本地: ~/.nanobot/media/image_xxx.jpg
     ↓
通知 Agent: "[Image downloaded to: /path/to/image.jpg]"
     ↓
同时将图片作为 vision input 发送给 LLM
```

### 2. Agent 可以使用图片

Agent 会收到两种形式的图片信息：
- **Vision Input**: 图片的 base64 编码（用于视觉理解）
- **本地路径**: 文本形式的路径信息（用于工具调用）

## 💡 使用示例

### 场景 1: LLM 直接识别图片

```
用户: [在飞书发送一张猫的图片]
用户: 这是什么？

机器人: 这是一只可爱的橘猫，看起来很健康...
```

**原理**: LLM 直接通过 vision 功能识别图片内容

### 场景 2: 基于图片生成新图片

```
用户: [在飞书发送图片]
用户: 把这张图片生成一个卡通版本

机器人:
  1. 识别图片内容（vision）
  2. 看到 "[Image downloaded to: /path/to/image.jpg]"
  3. 调用 image_generate 工具，使用 input_image 参数
  4. 生成新图片
  5. 发送回飞书
```

### 场景 3: 图片分析 + 处理

```
用户: [发送多张图片]
用户: 分析这些图片并生成一个总结报告

机器人:
  1. 自动下载所有图片
  2. 逐个分析内容
  3. 生成总结报告
  4. 可以引用本地路径进行进一步处理
```

### 场景 4: 直接要求基于图片操作

```
用户: [发送图片]
用户: 生成高档餐厅版本

机器人: [自动识别到图片路径 → 调用 image_generate → 发送结果]
```

## 📂 文件存储

所有下载的图片自动保存在：

```
~/.nanobot/media/
```

文件命名示例：
- `image_20260301_152030.jpg`
- `img_v3_027f_xxx.jpg`

## 🎯 关键特性

✅ **完全自动**：无需手动下载或配置
✅ **双重使用**：既支持 vision 识别，也支持工具调用
✅ **路径透明**：Agent 明确知道本地文件路径
✅ **支持多图**：一次发送多张图片都会自动下载
✅ **支持富文本**：post 消息中的嵌入图片也会自动下载

## 🧪 测试

启动 gateway：

```bash
nanobot gateway
```

在飞书中测试：

### 测试 1: 视觉识别

```
1. 发送一张图片
2. 问："这是什么？"
3. 机器人应该能识别图片内容
```

### 测试 2: 图片生成

```
1. 发送一张图片
2. 说："生成卡通版本"
3. 机器人应该生成并返回新图片
```

### 测试 3: 批量处理

```
1. 发送多张图片
2. 说："分析所有图片"
3. 机器人应该能处理所有图片
```

## 📊 技术细节

### 消息流程

```
Feishu Message (image)
    ↓
FeishuChannel._on_message()
    ↓
_download_and_save_media()
    ↓
生成:
  - media_paths: ["/path/to/image.jpg"]
  - content_parts: ["[Image downloaded to: /path/to/image.jpg]"]
    ↓
InboundMessage(
    content="[Image downloaded to: /path/to/image.jpg]",
    media=["/path/to/image.jpg"]
)
    ↓
AgentLoop._process_message()
    ↓
ContextBuilder.build_messages()
    ↓
构建 LLM 输入:
  {
    "role": "user",
    "content": [
      {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,xxx"}},
      {"type": "text", "text": "[Image downloaded to: /path/to/image.jpg]"}
    ]
  }
    ↓
LLM 可以:
  1. 通过 vision 看到图片
  2. 通过文本知道本地路径
  3. 调用工具时使用本地路径
```

### 相关代码

**自动下载** (`nanobot/channels/feishu.py`):
```python
# 第 731-740 行
elif msg_type in ("image", "audio", "file", "media"):
    file_path, content_text = await self._download_and_save_media(msg_type, content_json, message_id)
    if file_path:
        media_paths.append(file_path)
        # For images, tell the agent the local path explicitly
        if msg_type == "image":
            content_parts.append(f"[Image downloaded to: {file_path}]")
```

**Vision Input 构建** (`nanobot/agent/context.py`):
```python
# 第 122-138 行
def _build_user_content(self, text: str, media: list[str] | None):
    if not media:
        return text

    images = []
    for path in media:
        p = Path(path)
        mime, _ = mimetypes.guess_type(path)
        if not p.is_file() or not mime or not mime.startswith("image/"):
            continue
        b64 = base64.b64encode(p.read_bytes()).decode()
        images.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})

    if not images:
        return text
    return images + [{"type": "text", "text": text}]
```

## 🔧 配置要求

### 必需配置

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxx",
      "appSecret": "xxx"
    }
  }
}
```

### 可选配置（用于图片生成）

```json
{
  "agents": {
    "defaults": {
      "imageModel": "google/gemini-3.1-flash-image-preview"
    }
  },
  "providers": {
    "zenmux": {
      "apiKey": "YOUR_API_KEY",
      "imageApiBase": "https://zenmux.ai/api/vertex-ai"
    }
  }
}
```

## ⚠️ 注意事项

### 1. Vision 支持

确保你使用的 LLM 支持 vision 功能：
- ✅ Claude 3.x/4.x (Sonnet, Opus)
- ✅ GPT-4 Vision, GPT-4o
- ✅ Gemini Pro Vision, Gemini 2.0
- ❌ GPT-3.5 (不支持)

### 2. 图片大小

- 飞书图片会自动下载，无大小限制
- 但注意：Base64 编码后会占用 LLM 上下文
- 建议单张图片不超过 20MB

### 3. 存储空间

- 图片会累积在 `~/.nanobot/media/` 目录
- 定期清理旧图片以节省空间
- 或者在配置中设置自动清理策略

### 4. API 费用

- Vision API 调用通常比纯文本更贵
- 注意 API 配额和费用

## 🎨 高级用法

### 组合使用多个功能

```
用户: [发送图片A]
用户: [发送图片B]
用户: 对比这两张图片的风格，然后基于图片A生成一个图片B风格的版本

机器人:
  1. 自动下载图片A和图片B
  2. 通过 vision 对比两张图片
  3. 理解风格差异
  4. 调用 image_generate(input_image=图片A路径, prompt="采用图片B的风格")
  5. 返回生成的新图片
```

### 批量处理

```
用户: [发送10张图片]
用户: 把这些图片都生成成黑白风格

机器人:
  1. 自动下载全部10张图片
  2. 逐个调用 image_generate
  3. 返回所有生成的图片
```

## 🐛 故障排除

### 问题 1: 图片没有自动下载

**检查**:
1. 飞书 channel 是否启用
2. gateway 是否正常运行
3. 查看日志：`nanobot gateway --verbose`

### 问题 2: Agent 无法识别图片

**可能原因**:
1. 使用的 LLM 不支持 vision
2. 图片格式不支持（需要 JPEG, PNG, GIF, WebP）
3. 图片文件损坏

**解决**:
- 切换到支持 vision 的模型
- 检查图片格式
- 重新发送图片

### 问题 3: 路径不可用

**检查**:
1. 图片是否成功下载到 `~/.nanobot/media/`
2. 文件权限是否正确
3. 磁盘空间是否充足

## 📚 相关文档

- [图片生成指南](./IMAGE_GENERATION_GUIDE.md)
- [飞书图片下载工具](./FEISHU_IMAGE_DOWNLOAD_GUIDE.md)
- [功能总览](./NEW_FEATURES_SUMMARY.md)

## 🎉 总结

飞书图片自动下载功能让你可以：

✨ **无缝体验**：发送图片后直接对话，无需额外步骤
🎨 **强大组合**：Vision 识别 + 工具调用 + 图片生成
🚀 **高效处理**：批量图片自动处理
💡 **智能理解**：LLM 既能"看到"图片，又能"使用"图片

**现在就试试吧！** 在飞书中发送一张图片，然后说："生成一个卡通版本" 🎨

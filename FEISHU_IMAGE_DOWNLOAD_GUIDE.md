# 飞书图片下载功能使用指南

## 🎯 功能说明

新增了两个工具，让 nanobot 可以从飞书下载图片到本地：

1. **`feishu_download_image`**: 从飞书下载图片到本地
2. **`feishu_extract_image_key`**: 从飞书 URL 或内容中提取 image_key（辅助工具）

## 📋 前置要求

### 1. 启用飞书 Channel

确保在 `~/.nanobot/config.json` 中配置了飞书：

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

### 2. 飞书应用权限

确保你的飞书应用有以下权限：
- `im:message` (发送消息)
- `im:message:readonly` (读取消息)
- `im:resource` (访问消息资源，下载图片)

## 🚀 使用方法

### 方式 1: 在聊天中使用（最简单）

当用户在飞书中发送图片后，机器人会自动记录 `message_id` 和 `image_key`。你可以直接在对话中请求：

```
请下载刚才我发送的那张图片
```

或者提供具体信息：

```
请下载飞书图片，image_key 是 img_v3_027f_xxx，message_id 是 om_xxx
```

### 方式 2: 通过 Python 代码调用

```python
import asyncio
from nanobot.agent.tools.feishu import FeishuDownloadImageTool
from nanobot.config.loader import load_config

async def download_feishu_image():
    config = load_config()
    tool = FeishuDownloadImageTool(config)

    # 下载图片
    result = await tool.execute(
        image_key="img_v3_027f_xxx",
        message_id="om_xxx",
        filename="my_custom_name"  # 可选：自定义文件名
    )

    print(result)  # 输出本地文件路径

asyncio.run(download_feishu_image())
```

### 方式 3: 提取 image_key（辅助功能）

如果你只有飞书图片 URL 或包含 image_key 的内容：

```python
from nanobot.agent.tools.feishu import FeishuExtractImageKeyTool

async def extract_key():
    tool = FeishuExtractImageKeyTool()

    result = await tool.execute(
        url_or_content="https://xxx.feishu.cn/...?image_key=img_v3_027f_xxx"
    )

    print(result)  # 输出: Found image_key: img_v3_027f_xxx

asyncio.run(extract_key())
```

## 🔄 典型工作流

### 场景：下载飞书图片并用于 AI 图片生成

1. **用户在飞书发送图片**
2. **机器人下载到本地**
   ```
   请下载我刚发的图片
   ```
   机器人返回：
   ```
   已下载到：/Users/xxx/.nanobot/media/feishu/image_20260301.jpg
   ```

3. **使用本地图片生成新图片**
   ```
   请基于这张图片生成一个卡通风格的版本
   ```

完整对话示例：
```
用户: [发送图片]
机器人: 收到图片
用户: 请下载这张图片并生成一个高档餐厅版本
机器人: [调用 feishu_download_image] → 获得本地路径
       [调用 image_generate 带 input_image] → 生成新图片
       [发送新图片回飞书]
```

## 📂 文件存储位置

下载的图片默认保存在：
```
~/.nanobot/media/feishu/
```

示例文件名：
- 使用原文件名：`image_20260301_152030.jpg`
- 使用 image_key：`img_v3_027f_xxx.jpg`
- 自定义文件名：`my_custom_name.jpg`

## 🛠️ 工具参数说明

### `feishu_download_image`

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `image_key` | string | ✅ | 飞书图片 key（如 `img_v3_027f_xxx`） |
| `message_id` | string | ✅ | 包含该图片的消息 ID（如 `om_xxx`） |
| `filename` | string | ❌ | 自定义文件名（不含扩展名，扩展名会自动添加） |

**返回值**：本地文件路径（string）

### `feishu_extract_image_key`

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `url_or_content` | string | ✅ | 包含 image_key 的 URL 或内容 |

**返回值**：提取到的 image_key 或错误信息

## 🔍 如何获取 message_id 和 image_key？

### 方法 1: 从飞书消息事件中获取（推荐）

当用户在飞书发送图片时，机器人会收到消息事件，其中包含：
- `event.message.message_id`: 消息 ID
- `event.message.content.image_key`: 图片 key

机器人会自动解析这些信息。

### 方法 2: 从飞书后台日志查看

在 nanobot 日志中可以看到：
```
[INFO] Received Feishu message: message_id=om_xxx, type=image, image_key=img_v3_027f_xxx
```

### 方法 3: 通过飞书开放平台 API

使用飞书 API 获取历史消息：
```bash
curl -X GET \
  'https://open.feishu.cn/open-apis/im/v1/messages/:message_id' \
  -H 'Authorization: Bearer YOUR_TENANT_ACCESS_TOKEN'
```

## ⚠️ 注意事项

1. **权限要求**
   - 确保飞书应用有 `im:resource` 权限
   - 机器人必须能访问包含该图片的会话

2. **图片有效期**
   - 飞书图片可能有时效性，建议及时下载
   - 如果图片已过期，下载会失败

3. **错误处理**
   - 如果 image_key 或 message_id 无效，工具会返回错误信息
   - 检查飞书应用配置和权限

4. **文件大小**
   - 飞书图片下载没有大小限制
   - 但注意本地磁盘空间

## 🐛 故障排除

### 错误：`Feishu SDK not installed`
```bash
uv sync
uv tool install --editable . --force
```

### 错误：`Feishu channel not configured`

检查 `~/.nanobot/config.json`：
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

### 错误：`Failed to download image`

可能原因：
1. **image_key 或 message_id 无效**
   - 检查是否复制正确
   - 确认图片还在有效期内

2. **权限不足**
   - 检查飞书应用是否有 `im:resource` 权限
   - 确认机器人在该会话中有访问权限

3. **网络问题**
   - 检查网络连接
   - 查看 nanobot 日志获取详细错误

### 调试技巧

启动 gateway 时开启详细日志：
```bash
nanobot gateway --verbose
```

查看日志中的详细错误信息：
```
[ERROR] Failed to download Feishu image: code=xxx, msg=xxx, log_id=xxx
```

## 📚 相关文档

- [飞书开放平台 - 消息与群组](https://open.feishu.cn/document/server-docs/im-v1/message)
- [飞书开放平台 - 获取消息资源](https://open.feishu.cn/document/server-docs/im-v1/message-resource/get)
- [nanobot 图片生成指南](./IMAGE_GENERATION_GUIDE.md)

## 🎯 完整示例

### 场景：从飞书下载图片并生成新版本

```python
import asyncio
import json
from nanobot.agent.tools.feishu import FeishuDownloadImageTool
from nanobot.agent.tools.image import ImageGenerateTool
from nanobot.config.loader import load_config

async def download_and_generate():
    config = load_config()

    # Step 1: 下载飞书图片
    feishu_tool = FeishuDownloadImageTool(config)
    local_path = await feishu_tool.execute(
        image_key="img_v3_027f_xxx",
        message_id="om_xxx"
    )

    if local_path.startswith("Error"):
        print(f"下载失败: {local_path}")
        return

    print(f"✅ 已下载到: {local_path}")

    # Step 2: 使用下载的图片生成新图片
    image_tool = ImageGenerateTool(config)
    result = await image_tool.execute(
        prompt="Make this look like a fancy restaurant dish",
        model="google/gemini-3.1-flash-image-preview",
        input_image=local_path
    )

    data = json.loads(result)
    print(f"✅ 生成新图片: {data['files']}")

asyncio.run(download_and_generate())
```

输出：
```
✅ 已下载到: /Users/xxx/.nanobot/media/feishu/image_20260301_152030.jpg
✅ 生成新图片: ['/Users/xxx/Desktop/nanobot/images/fancy_dish_20260301_152100_0.png']
```

# 飞书图片下载 - 快速参考

## ⚡️ 快速开始

### 1. 配置检查

确保 `~/.nanobot/config.json` 中已配置飞书：

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

### 2. 启动 Gateway

```bash
nanobot gateway
```

### 3. 在飞书中使用

发送图片后，直接说：

```
请下载刚才的图片
```

或者组合使用：

```
下载我刚发的图片并生成一个卡通版本
```

## 🛠️ 可用工具

### `feishu_download_image`

下载飞书图片到本地

**参数：**
- `image_key` (必需): 图片 key，如 `img_v3_027f_xxx`
- `message_id` (必需): 消息 ID，如 `om_xxx`
- `filename` (可选): 自定义文件名

**返回：** 本地文件路径

### `feishu_extract_image_key`

从 URL 或内容提取 image_key

**参数：**
- `url_or_content` (必需): 包含 image_key 的内容

**返回：** 提取的 image_key

## 📁 存储位置

```
~/.nanobot/media/feishu/
```

## 🔄 典型场景

### 场景 1: 简单下载

```
用户: [发送图片]
用户: 请下载这张图片
机器人: 已下载到 /Users/xxx/.nanobot/media/feishu/image.jpg
```

### 场景 2: 下载 + 图片生成

```
用户: [发送图片]
用户: 请把这张图片生成一个高档餐厅版本
机器人: [自动下载] → [生成新图片] → [发送回飞书]
```

### 场景 3: 批量处理

```
用户: [发送多张图片]
用户: 请把这些图片都生成卡通风格
机器人: [逐个下载] → [批量生成] → [返回结果]
```

## 🧪 测试

```bash
# 运行测试
uv run python test_feishu_download.py

# 查看详细指南
cat FEISHU_IMAGE_DOWNLOAD_GUIDE.md
```

## ⚠️ 常见问题

**Q: 如何获取 image_key 和 message_id？**
A: 机器人会自动从飞书消息中获取。你也可以查看 gateway 日志。

**Q: 下载失败怎么办？**
A: 检查：
1. 飞书配置是否正确
2. 应用是否有 `im:resource` 权限
3. 图片是否还在有效期内

**Q: 可以下载历史图片吗？**
A: 可以，只要有 image_key 和 message_id，且图片未过期。

## 📚 完整文档

详细使用说明请查看：`FEISHU_IMAGE_DOWNLOAD_GUIDE.md`

## 🎯 实用示例

### Python 调用

```python
from nanobot.agent.tools.feishu import FeishuDownloadImageTool
from nanobot.config.loader import load_config

async def download():
    config = load_config()
    tool = FeishuDownloadImageTool(config)

    path = await tool.execute(
        image_key="img_v3_027f_xxx",
        message_id="om_xxx"
    )

    print(f"Downloaded: {path}")
```

### 组合图片生成

```python
# 1. 下载飞书图片
local_path = await feishu_tool.execute(
    image_key="img_v3_027f_xxx",
    message_id="om_xxx"
)

# 2. 生成新图片
result = await image_tool.execute(
    prompt="Make it fancy",
    input_image=local_path
)
```

---

**💡 提示：** 机器人会智能识别你的意图，自动调用相应的工具。只需用自然语言描述你的需求即可！

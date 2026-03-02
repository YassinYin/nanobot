# 🎉 新功能总结

本次更新添加了三个重要功能，让 nanobot 具备更强大的图片处理能力！

## ✨ 新增功能

### 1. 🎨 图片+文本生成图片 (Image-to-Image)

**功能描述：** 基于输入图片和文本提示生成新图片

**使用方式：**
```python
# 聊天中使用
"请基于 /path/to/image.png 生成一个卡通风格的版本"

# 代码调用
await image_tool.execute(
    prompt="Make it cartoon style",
    model="google/gemini-3.1-flash-image-preview",
    input_image="/path/to/input.png"  # 新参数！
)
```

**支持格式：** PNG, JPEG, GIF, WebP

**详细文档：** [IMAGE_GENERATION_GUIDE.md](./IMAGE_GENERATION_GUIDE.md)

---

### 2. 📥 飞书图片下载 (Feishu Image Download)

**功能描述：** 从飞书下载图片到本地

**新增工具：**
- `feishu_download_image`: 下载图片
- `feishu_extract_image_key`: 提取 image_key

**使用方式：**
```python
# 聊天中使用
用户: [在飞书发送图片]
用户: "请下载刚才的图片"

# 代码调用
path = await feishu_tool.execute(
    image_key="img_v3_027f_xxx",
    message_id="om_xxx"
)
```

**存储位置：** `~/.nanobot/media/feishu/`

**详细文档：** [FEISHU_IMAGE_DOWNLOAD_GUIDE.md](./FEISHU_IMAGE_DOWNLOAD_GUIDE.md)

---

### 3. 🔐 增强的沙箱安全 (Enhanced Sandbox Security)

**功能描述：** 修复了目录限制绕过漏洞

**安全改进：**
- ✅ 拦截波浪号扩展 (`~`)
- ✅ 拦截环境变量 (`$HOME`, `$USER`)
- ✅ 拦截命令替换 (`` `command` ``, `$(command)`)
- ✅ 增强路径穿越检测 (`../`, `/..`)

**配置示例：**
```json
{
  "tools": {
    "allowedDirs": [
      "/Users/xxx/allowed_dir1",
      "/Users/xxx/allowed_dir2"
    ]
  }
}
```

**受保护的工具：**
- `exec` (shell 命令)
- `read_file`
- `write_file`
- `edit_file`
- `list_dir`

---

## 🔄 完整工作流示例

### 场景：从飞书下载图片并生成新版本

```
1. 用户在飞书发送图片
   用户: [发送图片]

2. 用户请求生成新版本
   用户: "请下载这张图片并生成一个高档餐厅版本"

3. 机器人自动处理
   - 调用 feishu_download_image 下载到本地
   - 调用 image_generate(input_image=本地路径)
   - 发送生成的图片回飞书

4. 完成
   机器人: [发送新生成的图片]
```

## 📦 安装 & 更新

```bash
# 同步依赖
uv sync

# 重新安装全局工具
uv tool install --editable . --force

# 启动 gateway
nanobot gateway
```

## 🧪 测试

```bash
# 测试图片生成
uv run python test_image_generation.py

# 测试飞书下载
uv run python test_feishu_download.py
```

## 📋 配置要求

### 图片生成功能

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

### 飞书图片下载

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

### 沙箱安全

```json
{
  "tools": {
    "restrictToWorkspace": false,
    "allowedDirs": [
      "/Users/xxx/allowed_dir1",
      "/Users/xxx/allowed_dir2"
    ]
  }
}
```

## 📚 文档索引

| 功能 | 快速参考 | 详细指南 |
|------|---------|----------|
| 图片生成 | - | [IMAGE_GENERATION_GUIDE.md](./IMAGE_GENERATION_GUIDE.md) |
| 飞书下载 | [FEISHU_QUICK_REFERENCE.md](./FEISHU_QUICK_REFERENCE.md) | [FEISHU_IMAGE_DOWNLOAD_GUIDE.md](./FEISHU_IMAGE_DOWNLOAD_GUIDE.md) |
| 沙箱安全 | - | 见上文"增强的沙箱安全"部分 |

## 🎯 实用技巧

### 技巧 1: 链式操作

```
"下载飞书图片 → 生成卡通版本 → 再生成油画版本"
```

机器人会自动识别并执行整个流程。

### 技巧 2: 批量处理

```
用户: [发送多张图片]
用户: "把这些图片都生成高档餐厅版本"
```

机器人会批量下载和生成。

### 技巧 3: 自定义风格

```
"基于这张图片生成：
1. 卡通风格
2. 油画风格
3. 黑白风格"
```

机器人会生成三个不同风格的版本。

## ⚠️ 注意事项

1. **图片生成**
   - 目前仅 Google Gemini 模型支持 image-to-image
   - 注意 API 调用配额和费用

2. **飞书下载**
   - 确保飞书应用有 `im:resource` 权限
   - 图片可能有时效性，建议及时下载

3. **沙箱安全**
   - 配置 `allowedDirs` 后会严格限制文件访问
   - 某些合法命令可能被拦截（如使用 `~` 的命令）

## 🐛 故障排除

### 问题 1: google-genai 未安装

```bash
uv sync
uv tool install --editable . --force
```

### 问题 2: 飞书下载失败

检查：
1. 飞书配置是否正确
2. 应用权限（需要 `im:resource`）
3. image_key 和 message_id 是否有效

### 问题 3: 沙箱拦截合法命令

临时方案：将目标目录添加到 `allowedDirs`

长期方案：使用文件工具（`read_file`, `write_file`）而非 shell 命令

## 🚀 后续计划

- [ ] 支持更多图片模型的 image-to-image
- [ ] 支持飞书视频下载
- [ ] 支持其他平台（钉钉、企业微信）的媒体下载
- [ ] 更细粒度的沙箱控制

## 💬 反馈

如有问题或建议，请：
- 查看详细文档
- 运行测试脚本
- 检查 nanobot 日志（`nanobot gateway --verbose`）
- 提交 Issue 到 GitHub

---

**🎉 享受新功能！** 如有任何问题，随时查看详细文档或运行测试脚本。

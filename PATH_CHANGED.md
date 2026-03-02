# 📁 飞书图片保存路径已修改

## ✅ 修改完成

飞书接收的图片现在会保存到：

```
/Users/yinrongjie/Desktop/nanobot/receiv_img/
```

## 📝 修改内容

### 修改 1: 飞书 Channel 自动下载路径

**文件**: `nanobot/channels/feishu.py`

**修改前**:
```python
media_dir = Path.home() / ".nanobot" / "media"
```

**修改后**:
```python
media_dir = Path("/Users/yinrongjie/Desktop/nanobot/receiv_img")
```

### 修改 2: 飞书下载工具路径

**文件**: `nanobot/agent/tools/feishu.py`

**修改前**:
```python
self._output_dir = Path.home() / ".nanobot" / "media" / "feishu"
```

**修改后**:
```python
self._output_dir = Path("/Users/yinrongjie/Desktop/nanobot/receiv_img")
```

## 🎯 影响范围

所有从飞书接收的图片（包括自动下载和手动下载）都会保存到新路径：

✅ 自动下载的图片（用户在飞书发送图片）
✅ 使用 `feishu_download_image` 工具下载的图片
✅ Post 消息中的嵌入图片

## 📂 目录结构

```
/Users/yinrongjie/Desktop/nanobot/
├── images/           # AI 生成的图片（未改变）
└── receiv_img/       # 从飞书接收的图片（新路径）
    ├── image_20260301_180530.jpg
    ├── image_20260301_180645.png
    └── ...
```

## 🚀 立即生效

修改已经生效！现在你可以：

1. **启动 gateway**
   ```bash
   nanobot gateway
   ```

2. **在飞书发送图片**
   - 图片会自动下载到 `/Users/yinrongjie/Desktop/nanobot/receiv_img/`

3. **查看下载的图片**
   ```bash
   ls /Users/yinrongjie/Desktop/nanobot/receiv_img/
   ```

## 📊 完整流程

```
飞书发送图片
    ↓
自动下载到: /Users/yinrongjie/Desktop/nanobot/receiv_img/
    ↓
告知 Agent 路径
    ↓
Agent 可以使用图片
    ↓
生成新图片保存到: /Users/yinrongjie/Desktop/nanobot/images/
```

## 🔍 验证

### 方法 1: 发送图片测试

1. 在飞书发送一张图片
2. 检查目录：
   ```bash
   ls -lt /Users/yinrongjie/Desktop/nanobot/receiv_img/ | head -5
   ```
3. 应该能看到新下载的图片

### 方法 2: 使用工具测试

```python
from nanobot.agent.tools.feishu import FeishuDownloadImageTool
from nanobot.config.loader import load_config

async def test():
    config = load_config()
    tool = FeishuDownloadImageTool(config)

    # 工具的 _output_dir 应该是新路径
    print(f"保存路径: {tool._output_dir}")
    # 输出: 保存路径: /Users/yinrongjie/Desktop/nanobot/receiv_img
```

## ⚙️ 如果需要修改路径

如果将来想要改回或修改为其他路径，修改这两个文件：

1. `nanobot/channels/feishu.py` - 第 569 行
2. `nanobot/agent/tools/feishu.py` - 第 31 行

然后重新安装：
```bash
uv tool install --editable . --force
```

## 📝 注意事项

1. **旧图片位置**
   - 之前下载在 `~/.nanobot/media/` 的图片不会自动移动
   - 如需要可以手动移动：
     ```bash
     mv ~/.nanobot/media/* /Users/yinrongjie/Desktop/nanobot/receiv_img/
     ```

2. **生成图片位置**
   - AI 生成的图片仍然保存在 `~/Desktop/nanobot/images/`
   - 这是在 `nanobot/agent/tools/image.py` 中定义的
   - 如需修改请告诉我

3. **目录权限**
   - 确保目录有写入权限
   - 当前权限：`drwxr-xr-x`（可读写）

4. **磁盘空间**
   - 注意 Desktop 目录的磁盘空间
   - 建议定期清理旧图片

## ✅ 测试结果

✓ 目录已创建
✓ 权限正确
✓ 代码已更新
✓ 工具已重新安装

**一切就绪！现在可以开始使用了。** 🎉

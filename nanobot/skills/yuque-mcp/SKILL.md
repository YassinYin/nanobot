---
name: yuque-mcp
description: "Operate Yuque (语雀) docs and knowledge bases through MCP tools. Use when users ask to search/read/create/update Yuque documents, manage knowledge bases, or sync content to/from Yuque."
homepage: https://github.com/yuque/yuque-mcp-server
metadata: {"nanobot":{"emoji":"📘","requires":{"bins":["npx"]},"install":[{"id":"brew-node","kind":"brew","formula":"node","bins":["node","npx"],"label":"Install Node.js (brew)"},{"id":"apt-nodejs","kind":"apt","package":"nodejs","bins":["node","npx"],"label":"Install Node.js (apt)"}]}}
---

# Yuque MCP

Use Yuque via MCP instead of manual browser steps.

## MCP Setup (nanobot)

Add this to `~/.nanobot/config.json`:

```json
{
  "tools": {
    "mcpServers": {
      "yuque": {
        "command": "npx",
        "args": ["-y", "yuque-mcp@latest"],
        "env": {
          "YUQUE_PERSONAL_TOKEN": "your_yuque_token"
        },
        "toolTimeout": 120
      }
    }
  }
}
```

Then restart nanobot so MCP tools are discovered again.

## Token Notes

- Preferred env var: `YUQUE_PERSONAL_TOKEN`
- Server also supports `YUQUE_TOKEN` and `YUQUE_GROUP_TOKEN`
- Generate token in Yuque personal settings and grant least required scope

## Operating Rules

1. Prefer Yuque MCP tools (`mcp_yuque_*`) for Yuque tasks.
2. For updates/deletes, first read the current document, then ask for confirmation before destructive actions.
3. Always include identifiers (group/login, book slug/id, doc id/slug) from lookup results instead of guessing names.
4. If user intent is ambiguous, do a search/list step first and present candidates.
5. After write operations, report what changed and the target document link or identifier.

## Typical User Requests

- "在语雀里搜索‘发布流程’文档。"
- "把这段内容更新到语雀《产品周报》今天的文档。"
- "新建一个语雀文档，标题是《Q2 复盘》。"
- "读取这个语雀文档并总结重点。"

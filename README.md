# lark-connector

A Claude Code Skill that gives Claude full control over Feishu (Lark) — documents, wikis, bitable, search, and node management — via MCP tools and Python scripts with OAuth token management.

## Features

- **Document read/write** — fetch, create, update Feishu docs and wiki pages (via MCP)
- **Search** — search wiki nodes and cloud documents
- **Wiki node management** — list, create, move, rename nodes; move cloud docs into wiki
- **Bitable** — create, query, update multi-dimensional tables
- **OAuth management** — automatic token acquisition, refresh, and validity checks

## Requirements

- Python 3.8+
- `pip install python-dotenv requests`
- A Feishu enterprise self-built app with these permissions:
  - `bitable:app`
  - `offline_access`
  - `wiki:wiki:readonly`
  - `search:docs:read`
  - `wiki:node:create`
  - `wiki:node:move`
  - `wiki:node:update`
- Redirect URL registered in app security settings: `http://localhost:8081/callback`

## Installation

### One-liner

```bash
curl -fsSL https://raw.githubusercontent.com/Bicool/lark-connector/main/install.sh | bash
```

### Manual

```bash
# Clone to Claude Code skills directory
git clone https://github.com/Bicool/lark-connector ~/.claude/skills/lark-connector

# Install dependencies
pip install python-dotenv requests

# Copy config template
cp ~/.claude/skills/lark-connector/assets/.env.example \
   ~/.claude/skills/lark-connector/assets/.env
```

## Configuration

Edit `~/.claude/skills/lark-connector/assets/.env`:

```
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxx
FEISHU_USER_ACCESS_TOKEN=    # auto-filled
FEISHU_REFRESH_TOKEN=        # auto-filled
```

Get App ID / App Secret: [Feishu Developer Console](https://open.feishu.cn/app) → App Details → Credentials

## Authorization

```bash
python ~/.claude/skills/lark-connector/scripts/authen_get_user_access_token.py
```

This opens a browser for OAuth. The token is saved to `assets/.env` automatically.

## Usage

Once installed, describe your Feishu task in Claude Code and it handles the rest:

```
"List all nodes in the AI加油站 wiki space"
"Create a new bitable named Sales Q2"
"Search for the project management bitable"
"Move the Claude docs into the 工具分类 wiki folder"
"Rename node wikcnXXX to SubAgent 机制"
```

## Directory Structure

```
lark-connector/
├── SKILL.md                                # Claude Code Skill definition
├── install.sh                              # One-click installer
├── assets/
│   ├── .env.example                        # Config template
│   └── .env                               # Local config (not committed)
└── scripts/
    ├── check_token.py                      # Check token validity (OK/EXPIRED/MISSING)
    ├── authen_get_user_access_token.py     # OAuth authorization flow
    ├── authen_refresh_user_access_token.py # Refresh expired token
    ├── drive_search_doc.py                 # Search all accessible cloud docs
    ├── wiki_search.py                      # Search wiki nodes (preferred)
    ├── wiki_list_nodes.py                  # List child nodes in a wiki space
    ├── wiki_get_node.py                    # Get node info by token
    ├── wiki_create_node.py                 # Create a new wiki node
    ├── wiki_update_title.py                # Rename a wiki node
    ├── wiki_move_node.py                   # Move node (supports cross-space)
    ├── wiki_move_doc_to_wiki.py            # Move cloud doc into wiki
    ├── bitable_create_app.py               # Create a bitable
    ├── bitable_get_app.py                  # Get bitable info
    └── bitable_update_app.py               # Update bitable name
```

## How It Works

1. **MCP tools** handle document read/write, comments, and user lookup directly.
2. **Python scripts** handle everything else (search, wiki nodes, bitable) using `user_access_token`.
3. Before any script runs, `check_token.py` validates the token. If expired, Claude refreshes it automatically. If missing, Claude triggers the OAuth flow.
4. Search strategy: `wiki_search.py` first (accurate, scoped), fallback to `drive_search_doc.py` (broad, includes all accessible docs).

---

## 中文说明

这是一个 Claude Code Skill，让 Claude 可以操作飞书的文档、知识库、多维表格和搜索功能。

**安装方式：**
```bash
curl -fsSL https://raw.githubusercontent.com/Bicool/lark-connector/main/install.sh | bash
```

**前置配置：**
1. 在[飞书开发者后台](https://open.feishu.cn/app)创建自建应用
2. 开通所需权限（见上方 Requirements）
3. 安全设置中注册回调地址 `http://localhost:8081/callback`
4. 填写 `.env` 中的 App ID 和 App Secret
5. 运行 `authen_get_user_access_token.py` 完成首次授权

**完整使用攻略：** [飞书文档](https://www.feishu.cn/docx/KCATd5Rh5oXgXJxRJ8DcTrq7nwh)

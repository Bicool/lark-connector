---
name: lark-connector
description: 飞书（Lark）操作助手，覆盖所有飞书自动化需求：文档读写（MCP）、搜索云文档/知识库、知识空间节点管理（创建/查询/列举/移动/重命名）、将云文档移入知识库、多维表格增删改查、OAuth 授权与 token 自动刷新。文档操作优先调用飞书 MCP 工具；搜索、知识库节点、多维表格通过 Python 脚本执行。Use this skill for any Feishu/Lark task — documents, wikis, bitable, searching, or node management.
---

# Lark 飞书操作指南

## 能力概览

| 能力 | 方式 |
|------|------|
| 读取/创建/更新文档 | MCP: `fetch-doc` / `create-doc` / `update-doc` |
| 列出知识库子文档 | MCP: `list-docs` |
| 获取/添加评论 | MCP: `get-comments` / `add-comments` |
| 搜索用户 / 获取用户信息 | MCP: `search-user` / `get-user` |
| 获取文件/图片 | MCP: `fetch-file` |
| 搜索云文档 | 脚本: `drive_search_doc.py`（不用 MCP search-doc） |
| 搜索知识库（Wiki） | 脚本: `wiki_search.py` |
| 知识空间节点：创建/查询/列举/重命名/移动 | 脚本: `wiki_*.py` |
| 将云文档移入知识库 | 脚本: `wiki_move_doc_to_wiki.py` |
| 多维表格：创建/查询/更新 | 脚本: `bitable_*.py` |

---

## 环境要求

依赖：
```bash
pip install python-dotenv requests
```

配置文件 `assets/.env`：
```
FEISHU_APP_ID=            # 必填，飞书自建应用 App ID
FEISHU_APP_SECRET=        # 必填，飞书自建应用 App Secret
FEISHU_USER_ACCESS_TOKEN= # 自动写入
FEISHU_REFRESH_TOKEN=     # 自动写入
```

若 `FEISHU_APP_ID` 或 `FEISHU_APP_SECRET` 为空，请先到飞书开发者后台（https://open.feishu.cn/app）创建自建应用并填写。

所需应用权限：`bitable:app`、`offline_access`、`wiki:wiki:readonly`、`search:docs:read`、`wiki:node:create`、`wiki:node:move`、`wiki:node:update`

回调地址（安全设置中注册）：`http://localhost:8081/callback`

---

## Token 检查流程（执行任何脚本前必须执行）

```
python scripts/check_token.py
  -> OK      -> 直接执行目标脚本
  -> EXPIRED -> python scripts/authen_refresh_user_access_token.py -> 执行目标脚本
  -> MISSING -> python scripts/authen_get_user_access_token.py    -> 执行目标脚本
```

---

## 决策树

```
用户请求飞书操作
       |
是文档读写/评论/用户? -> 是 -> 调用对应 MCP 工具
       | 否
是搜索? -> 是 -> 检查 token -> wiki_search.py -> 无结果则 fallback drive_search_doc.py
       | 否
是知识库节点/多维表格? -> 是 -> 检查 token -> 执行对应脚本
       | 否
不支持，告知用户
```

---

## 脚本参考

### Token 管理

**`scripts/check_token.py`**
输出 `OK` / `EXPIRED` / `MISSING`，供决策是否需要刷新。

**`scripts/authen_get_user_access_token.py`**
首次授权，自动打开浏览器完成 OAuth，token 写入 `assets/.env`。

**`scripts/authen_refresh_user_access_token.py`**
用 refresh_token 自动刷新，结果写回 `assets/.env`。

---

### 搜索

搜索策略：**优先 wiki_search，无结果时 fallback 到 drive_search_doc**。

```
Step 1: wiki_search.py 搜知识库
        有结果 -> 返回
        无结果 -> Step 2
Step 2: drive_search_doc.py 搜全局云文档
        不传 owner_ids，搜当前用户有权限看到的所有文档（含他人共享）
```

**`scripts/wiki_search.py`** — 搜索知识库节点（优先使用）
```python
from scripts.wiki_search import search_wiki
result = search_wiki(
    query="项目",
    space_id="xxx",  # 可选，限定知识空间
    page_size=20,
)
# 返回: {"items": [...], "has_more": bool, "page_token": str}
# items 字段: node_id, obj_token, obj_type, title, url, space_id
```

**`scripts/drive_search_doc.py`** — 搜索全局云文档（fallback）
不传 owner_ids，搜索当前用户有权访问的所有文档（含模板库、他人共享）。
```python
from scripts.drive_search_doc import search_docs
result = search_docs(
    search_key="项目",
    count=10,                                # 0-50，默认 10
    docs_types=["doc", "sheet", "bitable"],  # 可选，不传则搜所有类型
    # 不传 owner_ids，搜所有有权限的文档
)
# 返回: {"docs_entities": [...], "has_more": bool, "total": int}
```

---

### 知识空间节点管理

**`scripts/wiki_list_nodes.py`** — 列出子节点
```python
from scripts.wiki_list_nodes import list_all_nodes
items = list_all_nodes(space_id)                        # 一级节点（自动翻页）
items = list_all_nodes(space_id, parent_node_token="wikcnXXX")  # 指定父节点下
# 每项字段: node_token, obj_token, obj_type, title, has_child, parent_node_token
```

**`scripts/wiki_get_node.py`** — 获取节点信息
```python
from scripts.wiki_get_node import get_node
node = get_node("wikcnXXX")               # 用 wiki node token
node = get_node("doccnXXX", obj_type="docx")  # 用云文档 token
# 返回: {node_token, obj_token, obj_type, title, space_id, ...}
```

**`scripts/wiki_create_node.py`** — 创建节点（需权限 `wiki:node:create`）
```python
from scripts.wiki_create_node import create_node
node = create_node(
    space_id="xxx",
    obj_type="docx",               # docx / sheet / bitable / mindnote / slides
    node_type="origin",            # origin（实体）| shortcut（快捷方式）
    parent_node_token="wikcnXXX",  # 可选，为空则为一级节点
    title="新文档标题",              # 可选
)
# 返回: {node_token, obj_token, obj_type, ...}
```

**`scripts/wiki_update_title.py`** — 更新节点标题（需权限 `wiki:node:update`，仅支持 doc/docx/快捷方式）
```python
from scripts.wiki_update_title import update_title
update_title(space_id, node_token, "新标题")
```

**`scripts/wiki_move_node.py`** — 移动节点，支持跨空间（需权限 `wiki:node:move`）
```python
from scripts.wiki_move_node import move_node
node = move_node(space_id, node_token,
                 target_parent_token="wikcnYYY",   # 可选
                 target_space_id="xxx")             # 可选，跨空间时指定
# 返回: 移动后的 node 对象
```

**`scripts/wiki_move_doc_to_wiki.py`** — 将云文档移入知识库（需权限 `wiki:node:move`）
移动后文档从云空间消失，改为知识库管理。
```python
from scripts.wiki_move_doc_to_wiki import move_doc_to_wiki
result = move_doc_to_wiki(space_id, "docx", "doccnXXX")
result = move_doc_to_wiki(space_id, "docx", "doccnXXX", parent_wiki_token="wikcnYYY")
# 返回: {"wiki_token": "..."} | {"task_id": "..."} | {"applied": True}
```

---

### 多维表格

**`scripts/bitable_create_app.py`** — 创建多维表格
```python
from scripts.bitable_create_app import create_app
app = create_app(name="表格名称", folder_token=None)
# 返回: {app_token, default_table_id, url}
```

**`scripts/bitable_get_app.py`** — 获取多维表格信息
```python
from scripts.bitable_get_app import get_app
app = get_app(app_token="xxx")
```

**`scripts/bitable_update_app.py`** — 更新多维表格名称
```python
from scripts.bitable_update_app import update_app
app = update_app(app_token="xxx", name="新名称")
```

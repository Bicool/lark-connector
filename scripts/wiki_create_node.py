import json
import os

from dotenv import load_dotenv
import requests

load_dotenv(os.path.join(os.path.dirname(__file__), "../assets/.env"))

BASE_URL = "https://open.feishu.cn/open-apis"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {os.environ['FEISHU_USER_ACCESS_TOKEN']}",
        "Content-Type": "application/json; charset=utf-8",
    }


def _check(resp: requests.Response) -> dict:
    resp.raise_for_status()
    data = resp.json()
    if data.get("code", 0) != 0:
        raise RuntimeError(json.dumps(data, indent=4, ensure_ascii=False))
    return data


def create_node(
    space_id: str,
    obj_type: str,
    node_type: str = "origin",
    parent_node_token: str = None,
    title: str = None,
    origin_node_token: str = None,
) -> dict:
    """
    在知识空间中创建节点。
    obj_type: docx / sheet / bitable / mindnote / slides
    node_type: origin（实体）| shortcut（快捷方式）
    parent_node_token: 父节点 token，为空则创建为一级节点
    title: 文档标题（可选）
    origin_node_token: 快捷方式对应的实体 node_token（node_type=shortcut 时必填）
    返回: node 对象，含 node_token, obj_token, obj_type 等字段
    """
    payload = {"obj_type": obj_type, "node_type": node_type}
    if parent_node_token:
        payload["parent_node_token"] = parent_node_token
    if title:
        payload["title"] = title
    if origin_node_token:
        payload["origin_node_token"] = origin_node_token
    data = _check(
        requests.post(
            f"{BASE_URL}/wiki/v2/spaces/{space_id}/nodes",
            headers=_headers(),
            json=payload,
        )
    )
    return data["data"]["node"]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python wiki_create_node.py <space_id> <obj_type> [parent_node_token] [title]")
        sys.exit(1)
    space_id = sys.argv[1]
    obj_type = sys.argv[2]
    parent = sys.argv[3] if len(sys.argv) > 3 else None
    title = sys.argv[4] if len(sys.argv) > 4 else None
    node = create_node(space_id, obj_type, parent_node_token=parent, title=title)
    print(json.dumps(node, indent=4, ensure_ascii=False))

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


def list_nodes(
    space_id: str,
    parent_node_token: str = None,
    page_size: int = 50,
    page_token: str = None,
) -> dict:
    """
    获取知识空间子节点列表（分页）。
    space_id: 知识空间 ID，或 "my_library" 表示我的文档库
    parent_node_token: 父节点 token，为空则获取一级节点
    返回: {"items": [...], "has_more": bool, "page_token": str}
    """
    params = {"page_size": page_size}
    if parent_node_token:
        params["parent_node_token"] = parent_node_token
    if page_token:
        params["page_token"] = page_token
    data = _check(
        requests.get(
            f"{BASE_URL}/wiki/v2/spaces/{space_id}/nodes",
            headers=_headers(),
            params=params,
        )
    )
    return data["data"]


def list_all_nodes(space_id: str, parent_node_token: str = None) -> list:
    """自动翻页，返回所有子节点列表。"""
    items = []
    page_token = None
    while True:
        result = list_nodes(space_id, parent_node_token, page_token=page_token)
        items.extend(result.get("items", []))
        if not result.get("has_more"):
            break
        page_token = result.get("page_token")
    return items


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python wiki_list_nodes.py <space_id> [parent_node_token]")
        sys.exit(1)
    space_id = sys.argv[1]
    parent = sys.argv[2] if len(sys.argv) > 2 else None
    items = list_all_nodes(space_id, parent)
    print(json.dumps(items, indent=4, ensure_ascii=False))

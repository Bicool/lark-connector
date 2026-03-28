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


def move_node(
    space_id: str,
    node_token: str,
    target_parent_token: str = None,
    target_space_id: str = None,
) -> dict:
    """
    移动知识空间节点，支持跨知识空间移动。子节点随之一起移动。
    space_id: 当前所在知识空间 ID
    node_token: 要移动的节点 token
    target_parent_token: 目标父节点 token，为空则移动为目标空间一级节点
    target_space_id: 目标知识空间 ID，为空则在当前空间内移动
    返回: 移动后的 node 对象
    """
    payload = {}
    if target_parent_token:
        payload["target_parent_token"] = target_parent_token
    if target_space_id:
        payload["target_space_id"] = target_space_id
    data = _check(
        requests.post(
            f"{BASE_URL}/wiki/v2/spaces/{space_id}/nodes/{node_token}/move",
            headers=_headers(),
            json=payload,
        )
    )
    return data["data"]["node"]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python wiki_move_node.py <space_id> <node_token> [target_parent_token] [target_space_id]")
        sys.exit(1)
    space_id = sys.argv[1]
    node_token = sys.argv[2]
    target_parent = sys.argv[3] if len(sys.argv) > 3 else None
    target_space = sys.argv[4] if len(sys.argv) > 4 else None
    node = move_node(space_id, node_token, target_parent, target_space)
    print(json.dumps(node, indent=4, ensure_ascii=False))

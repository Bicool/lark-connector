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


def get_node(token: str, obj_type: str = "wiki") -> dict:
    """
    获取知识空间节点信息。
    token: wiki 节点 token（URL 中 wiki/ 后的部分），或云文档实际 token
    obj_type: 默认 wiki；若传入云文档 token，需指定对应类型（docx/sheet/bitable 等）
    返回: node 对象，含 node_token, obj_token, obj_type, title, space_id 等字段
    """
    params = {"token": token}
    if obj_type != "wiki":
        params["obj_type"] = obj_type
    data = _check(
        requests.get(
            f"{BASE_URL}/wiki/v2/spaces/get_node",
            headers=_headers(),
            params=params,
        )
    )
    return data["data"]["node"]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python wiki_get_node.py <token> [obj_type]")
        sys.exit(1)
    token = sys.argv[1]
    obj_type = sys.argv[2] if len(sys.argv) > 2 else "wiki"
    node = get_node(token, obj_type)
    print(json.dumps(node, indent=4, ensure_ascii=False))

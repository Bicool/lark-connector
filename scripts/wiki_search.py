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


def search_wiki(
    query: str,
    space_id: str = None,
    node_id: str = None,
    page_size: int = 20,
    page_token: str = None,
) -> dict:
    """搜索知识库，返回 {"items": [...], "has_more": bool, "page_token": str}"""
    payload = {"query": query}
    if space_id:
        payload["space_id"] = space_id
    if node_id:
        payload["node_id"] = node_id
    params = {"page_size": page_size}
    if page_token:
        params["page_token"] = page_token
    data = _check(
        requests.post(
            f"{BASE_URL}/wiki/v2/nodes/search",
            headers=_headers(),
            params=params,
            json=payload,
        )
    )
    return data["data"]


if __name__ == "__main__":
    import sys

    keyword = sys.argv[1] if len(sys.argv) > 1 else "项目"
    result = search_wiki(keyword)
    print(json.dumps(result, indent=4, ensure_ascii=False))

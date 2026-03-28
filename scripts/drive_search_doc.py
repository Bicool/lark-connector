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


def search_docs(
    search_key: str,
    count: int = 10,
    offset: int = 0,
    owner_ids: list = None,
    chat_ids: list = None,
    docs_types: list = None,
) -> dict:
    """搜索云文档，返回 {"docs_entities": [...], "has_more": bool, "total": int}"""
    payload = {"search_key": search_key, "count": count, "offset": offset}
    if owner_ids:
        payload["owner_ids"] = owner_ids
    if chat_ids:
        payload["chat_ids"] = chat_ids
    if docs_types:
        payload["docs_types"] = docs_types
    data = _check(
        requests.post(
            f"{BASE_URL}/suite/docs-api/search/object",
            headers=_headers(),
            json=payload,
        )
    )
    return data["data"]


if __name__ == "__main__":
    import sys

    keyword = sys.argv[1] if len(sys.argv) > 1 else "项目"
    result = search_docs(keyword)
    print(json.dumps(result, indent=4, ensure_ascii=False))

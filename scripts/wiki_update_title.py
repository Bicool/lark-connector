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


def update_title(space_id: str, node_token: str, title: str) -> None:
    """
    更新知识空间节点标题。
    仅支持 doc、docx 和快捷方式节点。
    """
    _check(
        requests.post(
            f"{BASE_URL}/wiki/v2/spaces/{space_id}/nodes/{node_token}/update_title",
            headers=_headers(),
            json={"title": title},
        )
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: python wiki_update_title.py <space_id> <node_token> <title>")
        sys.exit(1)
    update_title(sys.argv[1], sys.argv[2], sys.argv[3])
    print("标题更新成功")

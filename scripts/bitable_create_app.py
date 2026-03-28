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


def create_app(name: str, folder_token: str = None) -> dict:
    payload = {"name": name}
    if folder_token:
        payload["folder_token"] = folder_token
    data = _check(requests.post(f"{BASE_URL}/bitable/v1/apps", headers=_headers(), json=payload))
    return data["data"]["app"]


if __name__ == "__main__":
    app = create_app("一篇新的多维表格")
    print(json.dumps(app, indent=4, ensure_ascii=False))

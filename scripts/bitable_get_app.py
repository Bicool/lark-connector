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


def get_app(app_token: str) -> dict:
    data = _check(requests.get(f"{BASE_URL}/bitable/v1/apps/{app_token}", headers=_headers()))
    return data["data"]["app"]


if __name__ == "__main__":
    app = get_app("appbcbWCzen6D8dezhoCH2RpMAh")
    print(json.dumps(app, indent=4, ensure_ascii=False))

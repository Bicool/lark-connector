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


def update_app(app_token: str, name: str = None, is_advanced: bool = None) -> dict:
    payload = {}
    if name is not None:
        payload["name"] = name
    if is_advanced is not None:
        payload["is_advanced"] = is_advanced
    data = _check(requests.put(f"{BASE_URL}/bitable/v1/apps/{app_token}", headers=_headers(), json=payload))
    return data["data"]["app"]


if __name__ == "__main__":
    app = update_app("appbcbWCzen6D8dezhoCH2RpMAh", name="新的多维表格名称")
    print(json.dumps(app, indent=4, ensure_ascii=False))

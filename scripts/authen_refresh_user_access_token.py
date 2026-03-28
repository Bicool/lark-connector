import json
import os
import re

from dotenv import load_dotenv
import requests

ENV_FILE = os.path.join(os.path.dirname(__file__), "../assets/.env")
load_dotenv(ENV_FILE)


def _save_tokens(data: dict) -> None:
    with open(ENV_FILE) as f:
        content = f.read()
    updates = {
        "FEISHU_USER_ACCESS_TOKEN": data["access_token"],
        "FEISHU_REFRESH_TOKEN": data.get("refresh_token", ""),
    }
    for key, value in updates.items():
        pattern = rf"^{key}=.*$"
        replacement = f"{key}={value}"
        if re.search(pattern, content, flags=re.MULTILINE):
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        else:
            content += f"\n{replacement}"
    with open(ENV_FILE, "w") as f:
        f.write(content)
    print("[+] token 已保存到 .env")


def refresh_user_access_token() -> dict:
    """
    刷新 user_access_token
    https://open.feishu.cn/document/authentication-management/access-token/refresh-user-access-token

    注意：
    - refresh_token 仅能使用一次，刷新后原 refresh_token 立即失效
    - 需要应用开通 offline_access 权限
    - 用户授权 365 天后必须重新授权
    """
    payload = {
        "grant_type": "refresh_token",
        "client_id": os.environ["FEISHU_APP_ID"],
        "client_secret": os.environ["FEISHU_APP_SECRET"],
        "refresh_token": os.environ["FEISHU_REFRESH_TOKEN"],
    }

    resp = requests.post(
        "https://open.feishu.cn/open-apis/authen/v2/oauth/token",
        headers={"Content-Type": "application/json; charset=utf-8"},
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("code", 0) != 0:
        raise RuntimeError(
            f"refresh_user_access_token failed: code={data.get('code')}, "
            f"error={data.get('error')}, desc={data.get('error_description')}"
        )

    _save_tokens(data)
    return data


if __name__ == "__main__":
    result = refresh_user_access_token()
    print(json.dumps(result, indent=4, ensure_ascii=False))

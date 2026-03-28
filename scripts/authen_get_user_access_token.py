import json
import os
import re
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

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


def get_user_access_token(code: str, redirect_uri: str = None) -> dict:
    """
    获取 user_access_token
    https://open.feishu.cn/document/authentication-management/access-token/get-user-access-token
    """
    payload = {
        "grant_type": "authorization_code",
        "client_id": os.environ["FEISHU_APP_ID"],
        "client_secret": os.environ["FEISHU_APP_SECRET"],
        "code": code,
    }
    if redirect_uri:
        payload["redirect_uri"] = redirect_uri

    resp = requests.post(
        "https://open.feishu.cn/open-apis/authen/v2/oauth/token",
        headers={"Content-Type": "application/json; charset=utf-8"},
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("code", 0) != 0:
        raise RuntimeError(
            f"get_user_access_token failed: code={data.get('code')}, "
            f"error={data.get('error')}, desc={data.get('error_description')}"
        )

    _save_tokens(data)
    return data


if __name__ == "__main__":
    REDIRECT_URI = "http://localhost:8081/callback"
    AUTH_URL = (
        f"https://accounts.feishu.cn/open-apis/authen/v1/authorize"
        f"?client_id={os.environ['FEISHU_APP_ID']}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=bitable:app%20offline_access%20wiki:wiki:readonly%20wiki:node:create%20search:docs:read"
        f"&response_type=code"
    )

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            params = parse_qs(urlparse(self.path).query)
            code = params.get("code", [None])[0]
            if not code:
                self.send_response(400); self.end_headers()
                return
            try:
                get_user_access_token(code=code, redirect_uri=REDIRECT_URI)
                body = b"<h2>Authorization successful! You can close this tab.</h2>"
                self.send_response(200)
            except Exception as e:
                body = f"<h2>Error: {e}</h2>".encode()
                self.send_response(500)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            threading.Thread(target=self.server.shutdown, daemon=True).start()

        def log_message(self, *args):
            pass

    print(f"[*] 打开浏览器授权：\n{AUTH_URL}\n")
    webbrowser.open(AUTH_URL)
    HTTPServer(("localhost", 8081), _Handler).serve_forever()

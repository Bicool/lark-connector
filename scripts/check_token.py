"""
检查 .env 中的 FEISHU_USER_ACCESS_TOKEN 是否有效。
输出 OK 或 EXPIRED，供 skill 决策是否需要刷新。
"""
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../assets/.env"), override=True)

token = os.environ.get("FEISHU_USER_ACCESS_TOKEN", "")
if not token:
    print("MISSING")
    sys.exit(1)

resp = requests.get(
    "https://open.feishu.cn/open-apis/authen/v1/user_info",
    headers={"Authorization": f"Bearer {token}"},
)
data = resp.json()
code = data.get("code", 0)

if code in (99991663, 99991664, 99991661) or resp.status_code == 401:
    print("EXPIRED")
    sys.exit(2)

print("OK")

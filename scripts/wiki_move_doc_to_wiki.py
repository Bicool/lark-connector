import json
import os
import time

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


def get_task_result(task_id: str) -> dict:
    """查询异步任务结果，返回 {"wiki_token": "..."} 或 {"status": "pending"}"""
    data = _check(
        requests.get(
            f"{BASE_URL}/wiki/v2/tasks/{task_id}",
            headers=_headers(),
            params={"task_type": "move_docs_to_wiki"},
        )
    )
    return data["data"]


def move_doc_to_wiki(
    space_id: str,
    obj_type: str,
    obj_token: str,
    parent_wiki_token: str = None,
    apply: bool = False,
    wait: bool = True,
    timeout: int = 30,
) -> dict:
    """
    将云空间文档移动至知识空间。异步接口，默认等待完成。
    space_id: 目标知识空间 ID
    obj_type: 文档类型（docx / doc / sheet / bitable / mindnote / file / slides）
    obj_token: 云文档 token
    parent_wiki_token: 挂载的父节点 token，为空则移动为一级节点
    apply: 无权限时是否申请移动（申请通过后自动移动）
    wait: 是否等待异步任务完成（默认 True）
    timeout: 最长等待秒数（默认 30）
    返回:
      {"wiki_token": "..."} — 移动完成
      {"task_id": "..."}   — 异步进行中（wait=False 时）
      {"applied": True}    — 已提交申请
    """
    payload = {"obj_type": obj_type, "obj_token": obj_token}
    if parent_wiki_token:
        payload["parent_wiki_token"] = parent_wiki_token
    if apply:
        payload["apply"] = apply
    data = _check(
        requests.post(
            f"{BASE_URL}/wiki/v2/spaces/{space_id}/nodes/move_docs_to_wiki",
            headers=_headers(),
            json=payload,
        )
    )["data"]

    # 已完成或已申请
    if "wiki_token" in data or "applied" in data:
        return data

    # 异步任务
    task_id = data.get("task_id")
    if not task_id or not wait:
        return data

    # 轮询等待
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = get_task_result(task_id)
        if result.get("task", {}).get("wiki_token"):
            return {"wiki_token": result["task"]["wiki_token"]}
        time.sleep(2)
    return {"task_id": task_id, "status": "timeout"}


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: python wiki_move_doc_to_wiki.py <space_id> <obj_type> <obj_token> [parent_wiki_token]")
        sys.exit(1)
    space_id = sys.argv[1]
    obj_type = sys.argv[2]
    obj_token = sys.argv[3]
    parent = sys.argv[4] if len(sys.argv) > 4 else None
    result = move_doc_to_wiki(space_id, obj_type, obj_token, parent_wiki_token=parent)
    print(json.dumps(result, indent=4, ensure_ascii=False))

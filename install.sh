#!/bin/bash
# lark-connector 一键安装脚本
# 用法: curl -fsSL https://raw.githubusercontent.com/Bicool/lark-connector/main/install.sh | bash

set -e

SKILL_DIR="$HOME/.claude/skills/lark-connector"
REPO="https://github.com/Bicool/lark-connector"
SETTINGS="$HOME/.claude/settings.json"

echo "[1/4] 克隆 lark-connector..."
if [ -d "$SKILL_DIR" ]; then
  echo "  已存在 $SKILL_DIR，执行更新..."
  git -C "$SKILL_DIR" pull
else
  git clone "$REPO" "$SKILL_DIR"
fi

echo "[2/4] 初始化 .env 配置..."
ENV_FILE="$SKILL_DIR/assets/.env"
if [ ! -f "$ENV_FILE" ] || [ ! -s "$ENV_FILE" ]; then
  cp "$SKILL_DIR/assets/.env" "$ENV_FILE" 2>/dev/null || true
  echo "  请填写 $ENV_FILE 中的 FEISHU_APP_ID 和 FEISHU_APP_SECRET"
else
  echo "  .env 已存在，跳过"
fi

echo "[3/4] 安装 Python 依赖..."
pip install python-dotenv requests --quiet

echo "[4/4] 注册到 Claude Code..."
mkdir -p "$HOME/.claude"
if [ ! -f "$SETTINGS" ]; then
  echo '{"permissions":{"additionalDirectories":[]}}' > "$SETTINGS"
fi
python3 - <<PYEOF
import json, sys
path = "$SETTINGS"
skill = "$SKILL_DIR"
with open(path) as f:
    cfg = json.load(f)
cfg.setdefault("permissions", {}).setdefault("additionalDirectories", [])
if skill not in cfg["permissions"]["additionalDirectories"]:
    cfg["permissions"]["additionalDirectories"].append(skill)
    with open(path, "w") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)
    print("  已添加到 additionalDirectories")
else:
    print("  已在 additionalDirectories 中，跳过")
PYEOF

echo ""
echo "安装完成！下一步："
echo "  1. 编辑 $ENV_FILE"
echo "     填写 FEISHU_APP_ID 和 FEISHU_APP_SECRET"
echo "  2. 运行授权："
echo "     python $SKILL_DIR/scripts/authen_get_user_access_token.py"
echo "  3. 重启 Claude Code 使 Skill 生效"

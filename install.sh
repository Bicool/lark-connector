#!/bin/bash
# lark-connector 一键安装脚本
# 用法: curl -fsSL https://raw.githubusercontent.com/Bicool/lark-connector/main/install.sh | bash

set -e

SKILL_DIR="$HOME/.claude/skills/lark-connector"
REPO="https://github.com/Bicool/lark-connector"

echo "[1/4] 克隆 lark-connector..."
if [ -d "$SKILL_DIR" ]; then
  echo "  已存在 $SKILL_DIR，执行更新..."
  git -C "$SKILL_DIR" pull
else
  git clone "$REPO" "$SKILL_DIR"
fi

echo "[2/4] 初始化 .env 配置..."
ENV_FILE="$SKILL_DIR/assets/.env"
if [ ! -f "$ENV_FILE" ]; then
  cp "$SKILL_DIR/assets/.env.example" "$ENV_FILE"
  echo "  已创建 $ENV_FILE，请填写 App ID 和 App Secret"
else
  echo "  .env 已存在，跳过"
fi

echo "[3/4] 安装 Python 依赖..."
pip install python-dotenv requests --quiet

echo "[4/4] 完成！"
echo ""
echo "下一步："
echo "  1. 编辑 $ENV_FILE"
echo "     填写 FEISHU_APP_ID 和 FEISHU_APP_SECRET"
echo "  2. 运行授权："
echo "     python $SKILL_DIR/scripts/authen_get_user_access_token.py"

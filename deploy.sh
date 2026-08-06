#!/bin/bash
# AI-RSS-Hub 部署脚本：固化"改代码 → 校验 → 重启 → 验证"流程
# 用法（sam 身份，在仓库目录执行）：./deploy.sh
# 可选：先传入 commit message 参数则自动提交推送，如 ./deploy.sh "fix: xxx"
set -euo pipefail
cd "$(dirname "$0")"

echo "==> [1/5] 语法校验"
venv/bin/python -m py_compile app/main.py app/api/routes.py app/crud.py \
    app/services/rss_fetcher.py app/services/summarizer.py app/config.py app/scheduler.py

if [ $# -ge 1 ]; then
    echo "==> [2/5] 提交并推送: $*"
    git add -A
    git commit -m "$*"
    git push
else
    echo "==> [2/5] 未提供 commit message，跳过提交（工作区保持现状）"
fi

echo "==> [3/5] 重启服务"
sudo -n systemctl restart ai-rss-hub.service
sleep 3

echo "==> [4/5] 健康检查"
[ "$(systemctl is-active ai-rss-hub)" = "active" ] || { echo "FAIL: 服务未运行"; exit 1; }
code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/health)
[ "$code" = "200" ] || { echo "FAIL: /api/health 返回 $code"; exit 1; }

echo "==> [5/5] 状态"
systemctl show ai-rss-hub -p NRestarts --value
echo "部署完成，health=200"

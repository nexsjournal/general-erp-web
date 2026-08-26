#!/usr/bin/env bash
# 启动 ERPNext 本地开发服务（前台运行，Ctrl+C 停止）
# 实际端口见 bench/sites/common_site_config.json（当前 web=8002, socketio=9002）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
# 依赖检查
lsof -iTCP:3307 -sTCP:LISTEN -n -P >/dev/null 2>&1 || { echo "MariaDB 未运行: launchctl load ~/Library/LaunchAgents/homebrew.mxcl.mariadb-erp.plist"; exit 1; }
lsof -iTCP:6379 -sTCP:LISTEN -n -P >/dev/null 2>&1 || { echo "Redis 未运行: brew services start redis"; exit 1; }
# 端口检查：避免与仍在运行的旧服务冲突
lsof -iTCP:8002 -sTCP:LISTEN -n -P >/dev/null 2>&1 && { echo "8002 已被占用：旧的 dev 服务可能仍在运行。请先停止（前台按 Ctrl+C，或 pkill -f 'honcho start'），再重新运行本脚本。"; exit 1; }
cd "$ROOT/bench"
# bench start 会由 honcho 自己拉起 bench 专属 redis（config/redis_*.conf），
# 先停掉 setup 阶段单独起的实例，避免端口冲突
for f in config/redis_*.conf; do
  [ -f "$f" ] || continue
  rport=$(awk '/^port/{print $2; exit}' "$f")
  [ -n "$rport" ] || continue
  rpid=$(lsof -tiTCP:"$rport" -sTCP:LISTEN 2>/dev/null || true)
  [ -n "$rpid" ] && kill "$rpid" 2>/dev/null || true
done
# 残留清理：honcho/foreman 被外部杀掉时可能漏杀 bench 子进程，
# 残留的 scheduler 会占着 config/scheduler_process 锁，导致新 scheduler 秒退、整组被拖死
pkill -f 'bench_helper frappe (schedule|worker)' 2>/dev/null || true
sleep 1
bench start

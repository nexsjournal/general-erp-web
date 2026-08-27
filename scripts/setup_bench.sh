#!/usr/bin/env bash
# ============================================================
# ERPNext (Frappe Bench) 本地开发环境一键初始化（macOS）
# 可重复执行：已完成的步骤会自动跳过。
# 用法: ./scripts/setup_bench.sh
# ============================================================
set -euo pipefail

# ------------------ 可配置项 ------------------
FRAPPE_REF="v16.32.0"             # frappe 框架版本（固定 tag，升级走专门流程）
ERPNEXT_REF="v16.33.0"            # erpnext 版本（固定 tag，与 frappe 配套）
SITE_NAME="general.erp.local"     # 站点名（相当于本地域名）
DB_HOST="127.0.0.1"
DB_PORT="3307"                    # ERPNext 专用 MariaDB 端口（避开你机器上已有的 MySQL 3306）
DB_ROOT_USER="frappe"             # 建库用的数据库账号
DB_ROOT_PASSWORD="frappe123"
ADMIN_PASSWORD="admin123"         # ERPNext 后台 admin 密码（本地开发用）
CUSTOM_APP="general_erp"          # 我们的自定义 app（后续功能都加在这里）
MARIADB_CNF="/opt/homebrew/etc/mariadb-erp.cnf"
# ---------- 加速镜像（网络不佳时自动生效；清空则直连） ----------
GH_PROXY="https://gh-proxy.com/"                  # git clone 加速
PIP_MIRROR="https://pypi.tuna.tsinghua.edu.cn/simple"   # pip/uv 加速
NPM_MIRROR="https://registry.npmmirror.com"       # yarn/npm 加速

MARIADB_DATADIR="/opt/homebrew/var/mariadb"
LAUNCH_AGENT="$HOME/Library/LaunchAgents/homebrew.mxcl.mariadb-erp.plist"
# ------------------ 可配置项结束 ------------------

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BENCH_DIR="$ROOT/bench"
# frappe v16.32+ 要求 Python >= 3.14；自动检测本机可用的高版本 python
PYTHON_BIN=""
for p in /opt/homebrew/bin/python3.14 /opt/homebrew/bin/python3 /usr/local/bin/python3.14 "$(command -v python3 2>/dev/null || true)"; do
  [ -n "$p" ] && [ -x "$p" ] || continue
  if "$p" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 14) else 1)' 2>/dev/null; then
    PYTHON_BIN="$p"
    break
  fi
done
[ -n "$PYTHON_BIN" ] || { echo "需要 Python >= 3.14（brew install python 即可）"; exit 1; }
echo "使用 Python: $PYTHON_BIN ($("$PYTHON_BIN" --version 2>&1))"

log() { echo -e "\n\033[1;32m==> $*\033[0m"; }

command -v brew >/dev/null 2>&1 || { echo "需要先安装 Homebrew: https://brew.sh"; exit 1; }

# ---------- 1. 系统依赖 ----------
for f in python@3.11 mariadb redis; do
  brew list --formula "$f" >/dev/null 2>&1 || { log "安装依赖: $f"; brew install "$f"; }
done
[ -x "$PYTHON_BIN" ] || { echo "找不到 $PYTHON_BIN"; exit 1; }
command -v node >/dev/null 2>&1 || { log "安装 node"; brew install node; }
command -v yarn >/dev/null 2>&1 || { log "安装 yarn"; brew install yarn; }

export PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
# GitHub 克隆加速（仅影响本脚本子进程，不改全局 git 配置）
if [ -n "$GH_PROXY" ]; then
  export GIT_CONFIG_COUNT=1
  export GIT_CONFIG_KEY_0="url.${GH_PROXY}https://github.com/.insteadOf"
  export GIT_CONFIG_VALUE_0="https://github.com/"
fi
[ -n "$PIP_MIRROR" ] && export PIP_INDEX_URL="$PIP_MIRROR" UV_INDEX_URL="$PIP_MIRROR" UV_DEFAULT_INDEX="$PIP_MIRROR"
[ -n "$NPM_MIRROR" ] && export npm_config_registry="$NPM_MIRROR"


# ---------- 2. bench CLI ----------
if ! command -v bench >/dev/null 2>&1; then
  command -v pipx >/dev/null 2>&1 || { log "安装 pipx"; brew install pipx; }
  log "安装 frappe-bench CLI"
  pipx install frappe-bench
  export PATH="$HOME/.local/bin:$PATH"
fi

# ---------- 3. Redis ----------
brew services list 2>/dev/null | awk '$1=="redis" && $2!="started"{exit 10}' || { log "启动 redis"; brew services start redis; }

# ---------- 4. MariaDB（ERP 专用实例，端口 ${DB_PORT}） ----------
port_listen() { lsof -iTCP:"$1" -sTCP:LISTEN -n -P >/dev/null 2>&1; }
if ! port_listen "$DB_PORT"; then
  [ -f "$MARIADB_CNF" ] || {
    log "生成 $MARIADB_CNF"
    cat > "$MARIADB_CNF" << CNF
[mariadbd]
datadir=$MARIADB_DATADIR
port=$DB_PORT
socket=/tmp/mariadb-erp.sock
bind-address=127.0.0.1
pid-file=/tmp/mariadb-erp.pid

[client]
port=$DB_PORT
socket=/tmp/mariadb-erp.sock
CNF
  }
  if [ ! -f "$MARIADB_DATADIR/mysql/user.MAD" ] && [ ! -d "$MARIADB_DATADIR/mysql" ]; then
    log "初始化 MariaDB 数据目录"
    mkdir -p "$MARIADB_DATADIR"
    /opt/homebrew/opt/mariadb/bin/mariadb-install-db --user="$USER" --defaults-file="$MARIADB_CNF"
  fi
  [ -f "$LAUNCH_AGENT" ] || {
    log "注册 LaunchAgent（开机自启）"
    cat > "$LAUNCH_AGENT" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>homebrew.mxcl.mariadb-erp</string>
  <key>ProgramArguments</key>
  <array>
    <string>/opt/homebrew/opt/mariadb/bin/mariadbd-safe</string>
    <string>--defaults-file=$MARIADB_CNF</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/tmp/mariadb-erp.out.log</string>
  <key>StandardErrorPath</key><string>/tmp/mariadb-erp.err.log</string>
</dict>
</plist>
PLIST
  }
  launchctl load "$LAUNCH_AGENT" 2>/dev/null || true
  sleep 6
fi

db_ok() { mariadb -h "$DB_HOST" -P "$DB_PORT" -u"$DB_ROOT_USER" -p"$DB_ROOT_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; }
if ! db_ok; then
  log "创建数据库账号 ${DB_ROOT_USER}（首次，用临时实例修授权表）"
  launchctl unload "$LAUNCH_AGENT" 2>/dev/null || true
  sleep 2
  /opt/homebrew/opt/mariadb/bin/mariadbd --defaults-file="$MARIADB_CNF" --skip-grant-tables --skip-networking &
  MPID=$!
  sleep 5
  mariadb --defaults-file="$MARIADB_CNF" -e "
    FLUSH PRIVILEGES;
    CREATE USER IF NOT EXISTS '$DB_ROOT_USER'@'localhost' IDENTIFIED BY '$DB_ROOT_PASSWORD';
    CREATE USER IF NOT EXISTS '$DB_ROOT_USER'@'127.0.0.1' IDENTIFIED BY '$DB_ROOT_PASSWORD';
    GRANT ALL PRIVILEGES ON *.* TO '$DB_ROOT_USER'@'localhost' WITH GRANT OPTION;
    GRANT ALL PRIVILEGES ON *.* TO '$DB_ROOT_USER'@'127.0.0.1' WITH GRANT OPTION;
    FLUSH PRIVILEGES;"
  kill "$MPID" 2>/dev/null; wait "$MPID" 2>/dev/null || true
  sleep 2
  launchctl load "$LAUNCH_AGENT" 2>/dev/null || true
  sleep 6
fi
db_ok || { echo "数据库账号不可用，请检查 MariaDB($DB_PORT 端口) 与授权"; exit 1; }
log "MariaDB OK (127.0.0.1:$DB_PORT)"

# ---------- 5. bench 初始化 ----------
cd "$ROOT"
if [ ! -d "$BENCH_DIR/apps/frappe" ]; then
  if [ -d "$BENCH_DIR" ]; then
    log "bench 目录不完整，先移走备份（不删除）"
    mv "$BENCH_DIR" "${BENCH_DIR}.broken.$(date +%s)"
  fi
  log "bench init（下载 frappe，约 3-10 分钟）"
  bench init --frappe-branch "$FRAPPE_REF" --python "$PYTHON_BIN" "$BENCH_DIR"
fi

cd "$BENCH_DIR"
if [ ! -d apps/erpnext ]; then
  log "拉取 erpnext（约 3-10 分钟）"
  bench get-app erpnext --branch "$ERPNEXT_REF"
fi

# 自定义 app（源码在项目 apps/ 下，已随代码分发；首次 bench init 后软链进 bench）
if [ ! -e "apps/$CUSTOM_APP" ]; then
  ln -sfn ../../apps/$CUSTOM_APP "apps/$CUSTOM_APP"
fi
grep -qx "$CUSTOM_APP" apps.txt 2>/dev/null || echo "$CUSTOM_APP" >> apps.txt

# bench 要求每个 app 目录本身是 git 仓库（App.setup_details 会 git.Repo 检查）；
# 从 GitHub 克隆整个项目后 app 只是普通文件，这里自动补一个本地仓库（幂等）
if [ ! -d "apps/$CUSTOM_APP/.git" ]; then
  log "为 $CUSTOM_APP 初始化本地 git（bench 要求）"
  ( cd "apps/$CUSTOM_APP" && git init -q && git add -A \
    && git -c user.name="${USER:-bench}" -c user.email="bench@local" commit -q -m "${CUSTOM_APP} app (local git repo required by bench)" )
fi

# ---------- 6. 依赖（venv 被复制/换机后此步会重建） ----------
if ! "$BENCH_DIR/env/bin/python" --version >/dev/null 2>&1; then
  log "重建 Python 虚拟环境"
  bench setup env --python "$PYTHON_BIN"
fi
log "安装/更新 Python 依赖（约 3-10 分钟）"
bench setup requirements

# ---------- 6.6 Procfile dev 补丁（幂等） ----------
# dev 模式下登录失败会 errprint 打印 traceback 到 web 进程 stdout，
# 走 honcho 管道时可能 BrokenPipe 导致接口 500；
# 把 web 输出重定向到 logs/，与官方模板 worker 行的做法一致
if [ -f Procfile ] && ! grep -q 'logs/web.log' Procfile; then
  log "补丁 Procfile: web 输出重定向到 logs/（避免 dev 模式 500）"
  sed -i '' 's|^web: bench serve.*|& 1>> logs/web.log 2>> logs/web.error.log|' Procfile
fi

# ---------- 6.5 bench 自带 redis（cache/queue，new-site 需要） ----------
if [ -d "$BENCH_DIR/config" ]; then
  for f in "$BENCH_DIR"/config/redis_*.conf; do
    [ -f "$f" ] || continue
    rport=$(awk '/^port/{print $2; exit}' "$f")
    if [ -n "$rport" ] && ! lsof -iTCP:"$rport" -sTCP:LISTEN -n -P >/dev/null 2>&1; then
      log "启动 bench redis ($rport)"
      redis-server "$f" --daemonize yes
    fi
  done
  sleep 2
fi

# ---------- 7. 站点 ----------
if [ ! -d "sites/$SITE_NAME" ]; then
  log "创建站点 $SITE_NAME"
  bench new-site "$SITE_NAME" \
    --admin-password "$ADMIN_PASSWORD" \
    --db-root-username "$DB_ROOT_USER" --db-root-password "$DB_ROOT_PASSWORD" \
    --db-host "$DB_HOST" --db-port "$DB_PORT"
  bench --site "$SITE_NAME" install-app erpnext
fi
bench --site "$SITE_NAME" list-apps 2>/dev/null | grep -qx "$CUSTOM_APP" \
  || { log "安装自定义 app $CUSTOM_APP"; bench --site "$SITE_NAME" install-app "$CUSTOM_APP"; }

# ---------- 7.5 站点业务初始化（基础主数据 + 公司 + 财年，幂等） ----------
log "站点业务初始化（ERPNext 基础数据/公司/财年）"
( cd "$BENCH_DIR" && ./env/bin/python "$ROOT/scripts/init_site_data.py" "$SITE_NAME" )

# ---------- 8. 前端资源 ----------
log "构建前端资源 bench build（约 2-5 分钟）"
bench build

cat << DONE

============================================================
✅ 初始化完成
  启动服务:  ./scripts/start_dev.sh
  访问:      http://localhost:8002   登录 Administrator / ${ADMIN_PASSWORD}（实际端口以 bench/sites/common_site_config.json 为准）
  登录说明:   frappe 按用户名(docname)匹配，必须用 Administrator，邮箱不行
  站点:      $SITE_NAME
  数据库:    127.0.0.1:$DB_PORT (账号 $DB_ROOT_USER)
  自定义代码: apps/$CUSTOM_APP  （功能都加在这里，别动 apps/frappe、apps/erpnext）
============================================================
DONE

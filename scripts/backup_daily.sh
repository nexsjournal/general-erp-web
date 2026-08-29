#!/bin/bash
# general-erp 每日数据备份（DB dump + 私有文件 + 站点配置）
# 备份到项目外的 ~/erp-backups/<时间戳>/，保留 14 天。
# launchd 每日 03:00 触发：~/Library/LaunchAgents/com.generalerp.daily-backup.plist
set -e
BENCH_DIR="/Users/god/Desktop/项目/github/general-erp/bench"
SITE="general.erp.local"
BACKUP_ROOT="$HOME/erp-backups"
RETAIN_DAYS=14
STAMP=$(date +%Y%m%d-%H%M%S)
OUT_DIR="$BACKUP_ROOT/$STAMP"
mkdir -p "$OUT_DIR"

# 1. 从 site_config.json 读 DB 连接（密码经环境变量传，不进日志）
SCF="$BENCH_DIR/sites/$SITE/site_config.json"
DB_NAME=$(python3 -c "import json;print(json.load(open('$SCF'))['db_name'])")
DB_HOST=$(python3 -c "import json;print(json.load(open('$SCF')).get('db_host','localhost'))")
DB_PORT=$(python3 -c "import json;print(json.load(open('$SCF')).get('db_port',3306))")
DB_USER=$(python3 -c "import json;print(json.load(open('$SCF')).get('db_user','root'))")
export MYSQL_PWD=$(python3 -c "import json;print(json.load(open('$SCF')).get('db_password',''))")

# 2. DB dump（--single-transaction 不锁表）
# 注意：必须用原生二进制完整路径。/opt/homebrew/bin/mariadb-dump 是转发到
# 已停用 erp-mariadb docker 容器的 wrapper，走它会报 container not running。
MARIADB_DUMP="/opt/homebrew/opt/mariadb/bin/mariadb-dump"
"$MARIADB_DUMP" --host="$DB_HOST" --port="$DB_PORT" --user="$DB_USER" \
  --single-transaction --result-file "$OUT_DIR/db_$SITE.sql" --databases "$DB_NAME" 2>>"$OUT_DIR/backup.log"
unset MYSQL_PWD

# 3. 站点私有文件（上传的图片/附件）
tar -czf "$OUT_DIR/files_$SITE.tgz" -C "$BENCH_DIR/sites/$SITE" private public/files 2>>"$OUT_DIR/backup.log"

# 4. 站点配置（含 DB 连接，随备份一起走，换机可恢复）
cp "$SCF" "$OUT_DIR/" 2>>"$OUT_DIR/backup.log"

# 5. 校验：dump 非空且含表定义
if [ ! -s "$OUT_DIR/db_$SITE.sql" ] || ! grep -q "CREATE TABLE" "$OUT_DIR/db_$SITE.sql"; then
  echo "[FAIL] $STAMP 数据库 dump 缺失或为空，见 $OUT_DIR/backup.log"
  exit 1
fi

# 6. 清理超过保留期的备份
find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -mtime +$RETAIN_DAYS -exec rm -rf {} + 2>/dev/null || true

echo "[OK] $STAMP 备份完成: $(du -sh "$OUT_DIR" | cut -f1) -> $OUT_DIR"

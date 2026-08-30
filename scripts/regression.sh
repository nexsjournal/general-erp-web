#!/bin/bash
# general-erp 一键回归: 环境自愈 -> 全模块E2E/金额链/报表/权限 -> 清理测试数据
# 用法: bash scripts/regression.sh  (项目根目录执行)
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BENCH="${BENCH:-$ROOT/bench}"
SITE_NAME="${ERP_SITE:-general.erp.local}"
PY="$BENCH/env/bin/python"
T="$ROOT/tests/regression"
RC=0

echo "==> [0/6] 环境自愈: 站点/服务检查"
(cd "$BENCH" && $PY -c "
import frappe
frappe.init(site='$SITE_NAME', sites_path='sites'); frappe.connect()
assert frappe.db.count('GL Entry') >= 0
print('site OK, GL Entry:', frappe.db.count('GL Entry'))
") 2>/dev/null || { echo 'FAIL: 站点不可用, 先修环境再回归(禁带病测试)'; exit 2; }

echo "==> [1/6] 清理旧测试数据"
(cd "$BENCH" && $PY "$T/cleanup.py") || RC=1

for t in test_chain.py test_fin_reports.py test_modules.py test_permissions.py test_approval_guard.py test_approval_wizard.py; do
  echo "==> 跑 $t"
  (cd "$BENCH" && $PY "$T/$t") || RC=1
done

echo "==> [6/6] 清理本轮测试数据"
(cd "$BENCH" && $PY "$T/cleanup.py") || RC=1

echo "============================"
if [ $RC -eq 0 ]; then echo 'REGRESSION PASS'; else echo 'REGRESSION FAIL (见上方 FAIL 行)'; fi
exit $RC

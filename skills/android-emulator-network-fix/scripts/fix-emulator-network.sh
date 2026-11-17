#!/usr/bin/env bash
# 修复 Android 模拟器"无法联网"：AOSP 默认网络校验探测 connectivitycheck.gstatic.com
# 在国内被墙 → 系统把网络标记为未校验 → App 判定无网络（Chrome 报 ERR_NETWORK_CHANGED）。
# 修法：把探测地址换成国内可达源 + 重启网络栈让探测重跑。
#
# 用法:
#   bash fix-emulator-network.sh                # 修复当前所有在跑的模拟器
#   bash fix-emulator-network.sh emulator-5556  # 只修指定设备
#
# 注意: 修改随 AVD 用户数据持久；wipe data 或新建 AVD 后需重跑本脚本。

set -euo pipefail

# 定位 adb：PATH 优先 → %LOCALAPPDATA%\Android\Sdk（Windows/Git Bash）→ ANDROID_HOME
if command -v adb >/dev/null 2>&1; then
  ADB="$(command -v adb)"
elif [ -n "${LOCALAPPDATA:-}" ]; then
  LA="$(cygpath -u "$LOCALAPPDATA" 2>/dev/null || echo "$LOCALAPPDATA")"
  ADB="$LA/Android/Sdk/platform-tools/adb.exe"
elif [ -n "${ANDROID_HOME:-}" ]; then
  ADB="$ANDROID_HOME/platform-tools/adb"
else
  echo "错误: 找不到 adb。请将其加入 PATH，或确认 Android SDK 已安装。" >&2
  exit 1
fi
[ -x "$ADB" ] || { echo "错误: adb 不存在或不可执行: $ADB" >&2; exit 1; }

HTTP_URL="http://connect.rom.miui.com/generate_204"
HTTPS_URL="https://connect.rom.miui.com/generate_204"
FALLBACK_URL="http://204.ustclug.org/generate_204"
OTHER_URL="http://www.gstatic.cn/generate_204"

devices=("$@")
if [ ${#devices[@]} -eq 0 ]; then
  # 所有在线的模拟器（多台同时跑时每台都要修，别只修一台）
  devices=($("$ADB" devices | awk '/^emulator/ && $2=="device" {print $1}'))
fi
if [ ${#devices[@]} -eq 0 ]; then
  echo "没有在线的模拟器"
  exit 0
fi

for s in "${devices[@]}"; do
  echo "===== $s ====="
  echo "AVD: $("$ADB" -s "$s" shell getprop ro.boot.qemu.avd_name)"

  echo "[1/3] 换网络校验探测地址 -> 国内源"
  "$ADB" -s "$s" shell settings put global captive_portal_http_url "$HTTP_URL"
  "$ADB" -s "$s" shell settings put global captive_portal_https_url "$HTTPS_URL"
  "$ADB" -s "$s" shell settings put global captive_portal_fallback_url "$FALLBACK_URL"
  "$ADB" -s "$s" shell settings put global captive_portal_other_http_urls "$OTHER_URL"

  echo "[2/3] 重启网络栈(svc wifi/data disable→enable, API36 上 AIRPLANE_MODE 广播会被拒)"
  "$ADB" -s "$s" shell svc wifi disable
  "$ADB" -s "$s" shell svc data disable
  sleep 3
  "$ADB" -s "$s" shell svc wifi enable
  "$ADB" -s "$s" shell svc data enable

  echo "[3/3] 等校验探测(20s)后验证..."
  sleep 20
  validated=$("$ADB" -s "$s" shell dumpsys connectivity | grep -oE "nc\{\[[^]]*\]" | grep -c "VALIDATED" || true)
  http=$("$ADB" -s "$s" shell "printf 'GET /generate_204 HTTP/1.1\r\nHost: connect.rom.miui.com\r\nConnection: close\r\n\r\n' | nc -w 8 connect.rom.miui.com 80 | head -1" || true)

  echo "  通过校验的网络数: ${validated:-0} (>=1 即可, 理想 2)"
  echo "  HTTP 实测: ${http:-无响应}"
  case "${http:-}" in
    *204*) echo "  结果: ✅ $s 联网正常";;
    *)     echo "  结果: ❌ HTTP 不通, 检查主机网络/防火墙, 或重启该模拟器后再跑一次";;
  esac
done

echo "完成。App/浏览器若仍显示无网络, 刷新页面或重启该 App 即可(ERR_NETWORK_CHANGED 是切换瞬间的一次性报错)。"

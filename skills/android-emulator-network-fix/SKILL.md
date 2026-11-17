---
name: android-emulator-network-fix
description: 修复 Android 模拟器（AVD/官方 Emulator）无法联网：真因多为 gstatic 网络校验被墙而非真断网。在用户报告模拟器/AVD 无网络、App 报网络不可用、上传失败、Chrome ERR_NETWORK_CHANGED、状态栏"未连接到互联网"、DNS/联网异常时使用。
---

# Android 模拟器联网修复

把"模拟器无法联网"的诊断与修复固化为一条流水线。绝大多数案例不是真断网，而是 Android 的网络校验（captive portal probe）探测被墙地址失败，导致系统把网络标记为"未校验"，App 层直接判定无网络。

## 适用症状

- 状态栏显示"未连接到互联网"或 WiFi 图标带感叹号
- App 报"网络不可用 / 无网络连接"，上传/下载全部失败
- Chrome 报 `ERR_NETWORK_CHANGED`（校验反复失败导致 WiFi/蜂窝来回切默认网络）
- 同一 AVD 在独立窗口正常、AS 内嵌面板异常（往往是两台 AVD 同时在跑，只修了一台）

## 诊断决策树（先诊断再动手）

1. **`adb devices` 确认几台在跑。** 多台同时运行时每台都要单独检查与修复（历史上踩过的坑：AS 内嵌与独立窗口各跑一个 AVD，只修一台）。
2. **别信 ping。** 模拟器 NAT 不转发 ICMP，`ping` 外网丢包是正常现象；也不可只看 DNS（模拟器 DNS 由主机代答，解析成功不代表外网可达）。必须测 TCP：
   ```bash
   # HTTP（期望返回 HTTP/1.1 204 No Content）
   adb -s <serial> shell "printf 'GET /generate_204 HTTP/1.1\r\nHost: connect.rom.miui.com\r\nConnection: close\r\n\r\n' | nc -w 8 connect.rom.miui.com 80 | head -1"
   # HTTPS（发送最小 TLS ClientHello，收到 ServerHello 字节即 443 通）
   printf '\x16\x03\x01\x00\x2d\x01\x00\x00\x29\x03\x03%.0s' | true   # 见下方完整十六进制
   ```
   443 完整测法（在宿主机拼好二进制再经管道送入模拟器内 nc）：
   ```bash
   HL="\x16\x03\x01\x00\x2d\x01\x00\x00\x29\x03\x03$(printf '\x5a%.0s' $(seq 32))\x00\x00\x02\x00\x2f\x01\x00"
   printf "$HL" | adb -s <serial> shell "nc -w 8 www.baidu.com 443 | head -c 5 | od -An -tx1"
   # 收到 "16 03 03 ..." 即 TLS ServerHello，443 连通
   ```
3. **判定：**
   - TCP 通（80/443 任一返回数据）但系统/App 说没网 → **校验问题** → 跑修复脚本
   - TCP 全不通 → **真断网** → 查主机网络/防火墙/VPN，或重启该模拟器后再测
   - 辅助确认：`adb -s <serial> shell dumpsys connectivity` 中各网络的 `nc{[...]}` 块是否含 `VALIDATED`

## 根因与修复原理

- AOSP 镜像默认探测 `connectivitycheck.gstatic.com/generate_204`（国内被墙）→ NetworkMonitor 校验失败 → 网络缺少 `NET_CAPABILITY_VALIDATED` → App 判定无网络
- 修复 = 把探测地址换成国内可达源 + 重启网络栈让探测重跑：
  ```bash
  adb -s <serial> shell settings put global captive_portal_http_url  "http://connect.rom.miui.com/generate_204"
  adb -s <serial> shell settings put global captive_portal_https_url "https://connect.rom.miui.com/generate_204"
  adb -s <serial> shell settings put global captive_portal_fallback_url "http://204.ustclug.org/generate_204"
  adb -s <serial> shell settings put global captive_portal_other_http_urls "http://www.gstatic.cn/generate_204"
  adb -s <serial> shell svc wifi disable && adb -s <serial> shell svc data disable
  sleep 3
  adb -s <serial> shell svc wifi enable && adb -s <serial> shell svc data enable
  # 等 20 秒让探测完成，再 dumpsys connectivity 验证 VALIDATED
  ```
- API 36 上 `adb shell am broadcast -a android.intent.action.AIRPLANE_MODE` 会被拒（SecurityException），一律用 `svc wifi/data` 切换

## 一键修复脚本

脚本路径以本技能基目录为准：`scripts/fix-emulator-network.sh`

```bash
bash "<技能基目录>/scripts/fix-emulator-network.sh"                # 修复所有在线模拟器
bash "<技能基目录>/scripts/fix-emulator-network.sh" emulator-5556  # 只修指定设备
```

脚本行为：定位 adb（PATH → `%LOCALAPPDATA%\Android\Sdk` → `ANDROID_HOME`）→ 逐台换探测地址 → `svc` 重启网络栈 → 等 20s → 输出每台"通过校验的网络数"与 HTTP 204 实测结论。adb 未安装时报错退出，不产生副作用。

## Agent 调用示例

用户报"模拟器没网"时：

1. 跑 `adb devices`，报告设备清单与 AVD 名（`getprop ro.boot.qemu.avd_name`）
2. 按"诊断决策树"用 `nc` 测 TCP，区分校验问题与真断网
3. 校验问题 → 用 Bash 跑 `scripts/fix-emulator-network.sh`（不带参数修全部），把每台的 VALIDATED 网络数与 HTTP 实测结果原样汇报
4. 修完提醒用户：浏览器/App 若仍显示无网络，刷新一次即可（`ERR_NETWORK_CHANGED` 是切换瞬间的一次性报错）

## 注意事项

- 探测地址设置存在 AVD 用户数据里，重启模拟器不丢；**wipe data 或新建 AVD 后会还原，需重跑脚本**
- 探测源实测可达（2026-11）：connect.rom.miui.com ✅、204.ustclug.org ✅、www.gstatic.cn ✅；若日后失效，替换为其他 `generate_204` 源即可
- App 要连宿主机上的后端服务，地址必须写 `10.0.2.2`（模拟器视角的宿主机），写 `localhost` 会连到模拟器自己
- 该脚本只动模拟器系统设置，不修改宿主机任何配置

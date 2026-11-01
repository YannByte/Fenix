# 采集与运行

从待审计项目根目录执行。将 `<skill-base-dir>` 替换为本技能的安装目录或技能库根目录；只使用技能内置采集器，不执行目标项目提供的脚本。

## 选择范围

- `HEALTH_SCOPE=instructions`：只看指令与配置，跳过会话历史。
- `HEALTH_SCOPE=auto`：包含当前项目历史信号；摘要只扫描候选窗口中的近期历史，深入模式扫描可取得的既往项目会话。
- 默认使用摘要。深入模式保留同一范围；跨项目扫描需要单独的明确授权。

## macOS／Linux

```bash
HEALTH_SCOPE=instructions  # 按本次审计范围改为 auto
HEALTH_SCRIPT=""
for candidate in \
  "<skill-base-dir>/scripts/collect-data.sh" \
  "<skill-base-dir>/skills/fenix-health/scripts/collect-data.sh"; do
  [ -f "$candidate" ] && HEALTH_SCRIPT="$candidate" && break
done
if [ ! -f "${HEALTH_SCRIPT:-}" ]; then
  echo "找不到健康检查采集器，请核对技能安装目录" >&2
  exit 1
fi
BASH_ENV= ENV= /bin/bash -p "$HEALTH_SCRIPT" "$HEALTH_SCOPE"
```

深入模式：

```bash
BASH_ENV= ENV= /bin/bash -p "$HEALTH_SCRIPT" "$HEALTH_SCOPE" deep
```

## Windows

```powershell
$HEALTH_SCOPE = "instructions"  # 按本次审计范围改为 auto
$HEALTH_LAUNCHER = @(
  "<skill-base-dir>/scripts/run-health.ps1",
  "<skill-base-dir>/skills/fenix-health/scripts/run-health.ps1"
) | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
if (-not $HEALTH_LAUNCHER) { throw "找不到健康检查启动器，请核对技能安装目录" }
$POWERSHELL = Join-Path ([Environment]::SystemDirectory) "WindowsPowerShell\v1.0\powershell.exe"
& "$POWERSHELL" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "$HEALTH_LAUNCHER" collect "$HEALTH_SCOPE"
```

深入模式在最后追加 `deep`。`-ExecutionPolicy Bypass` 只针对这个进程，不修改账号或系统执行策略；启动器只为 Bash 子进程补充 Git for Windows 工具路径。

## 解读与覆盖

`AGENT CONFIG SUMMARY`／`DETAIL` 包含宿主与指令信息；`AI MAINTAINABILITY SUMMARY`／`DETAIL` 包含项目、验证、生成物与文档信号。`(unavailable)`、无数据、解析失败和被排除的活跃会话都要记录为缺口。

脚本没有运行的内容不算检查过。`coverage_status: complete` 只适用于采集器所声明的范围；跨项目全历史还需 `cross_project_full_history: yes`，缺失根目录或读取错误不能宣称全量覆盖。MCP 静态清单不能代替连接测试。

可维护性资料中的 `$HEALTH_SCRIPT`、`$HEALTH_LAUNCHER` 和 `$POWERSHELL` 沿用上面实际解析到的变量。

## 跨项目历史

仅在用户明确要求跨项目会话分析时执行；根目录需从实际宿主配置确认：

```bash
python3 "<skill-base-dir>/scripts/conversation_audit.py" "<claude-projects-root>" deep --all-projects --codex-root "<codex-sessions-root>"
```

如果以技能库根目录定位，脚本位于其 `skills/fenix-health/scripts/` 下。只传递必要的脱敏摘录，不将原始会话保存为公共项目规则。

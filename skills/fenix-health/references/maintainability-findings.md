# 可维护性检查

摘要读取 `AI MAINTAINABILITY SUMMARY`，深入检查按需读取 `DETAIL`。配置问题见[配置审计](config-audit.md)；下面的变量先按[采集与运行](collection.md)解析。

## 判断证据

- `commands` 是发现到的命令，不证明检查实际执行。核对默认入口是否覆盖重要路径，跳过、空结果和仅打印成功的目标不算有效验证。
- `verifier_evidence` 缺失、`hollow_verifiers` 或 `wrapper_findings` 需要结合实际改动判断。只有重要风险需要验证却确实缺失时才报告，不因缺少 Makefile 或某种文件结构判为失败。
- `context_status: UNKNOWN` 需要继续核对约束与风险，`NOT_APPLICABLE` 不代表已全面验收。文件大小、TODO 数量和模块形状只是调查线索。
- 对生成物漂移、失效命令和规则不可达，指出实际位置、影响及最小修复。不要从采集器统计直接提出大范围重构。

## 规则与重复故障

从会话提炼规则时，先区分独立复发与同一次事件的复制、重试或转发。核对稳定约束、适用范围、证据、目标层级、可行验证与脱敏风险，不复制原始会话或评分报告。

项目命令和分发约定留在项目；可复用工作方法放在技能；个人偏好和单机事实按其授权范围保留。按宿主实际支持的机制，让专项规则只在相关任务中可达，不机械推荐某种 `paths` 字段或嵌套文件名。

需要调查重复修复时可读取近期提交并按区域归类；时间窗口由任务决定。同一前缀下的多个 fix 不等于同一故障，需核对具体原因。已公开缺陷缺少追踪或回归保护时，可以建议有明确用途的记录与检查，不要求每个项目都有事故台账或热点地图。

## 检查入口

从目标项目根目录执行，使用采集资料已解析的变量。

macOS／Linux 摘要与深入检查：

```bash
BASH_ENV= ENV= /bin/bash -p "${HEALTH_SCRIPT%/*}/check-maintainability.sh" . summary
BASH_ENV= ENV= /bin/bash -p "${HEALTH_SCRIPT%/*}/check-maintainability.sh" . deep
```

Windows 对应入口：

```powershell
& "$POWERSHELL" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "$HEALTH_LAUNCHER" maintainability . summary
& "$POWERSHELL" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "$HEALTH_LAUNCHER" maintainability . deep
```

按所选深度执行其中一个，不要求连续运行两个。

## 文档引用

核对指令、技能与文档中被任务依赖的路径，区分真实引用和示例。路径存在不代表目标语义仍然正确，还要确认它包含被引用的规则。

```bash
BASH_ENV= ENV= /bin/bash -p "${HEALTH_SCRIPT%/*}/check-doc-refs.sh" .
```

```powershell
& "$POWERSHELL" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "$HEALTH_LAUNCHER" doc-refs .
```

深入可维护性扫描还检查仓库 Markdown 本地链接。辅助检查有其可识别范围；不能从没有报错推断所有行内路径、章节或跨技能模式都有效。

## 过期验证输出

已有验证日志引用已删除工作树、临时文件或旧路径时，检查日志来源与当前入口：

```bash
BASH_ENV= ENV= /bin/bash -p "${HEALTH_SCRIPT%/*}/check-verifier-output.sh" . "<log-file>"
```

```powershell
& "$POWERSHELL" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "$HEALTH_LAUNCHER" verifier-output . "<log-file>"
```

只分析用户提供或本轮已有的日志，不为喂给检查器而运行项目测试。缓存清理是候选处置，实际执行需符合授权与证据，不能仅凭过期路径就删除缓存。

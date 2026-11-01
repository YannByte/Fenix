# Logging Techniques for Debugging

Every log answers a yes/no question about a hypothesis: "if this prints X before Y, hypothesis A holds; otherwise A is dead." A log that cannot rule a hypothesis in or out is noise.

## Discriminating Content

Log what discriminates between hypotheses: ordering (sequence number or timestamp), input identity key, branch taken, old-vs-new state transition, and error code plus context. Place logs at boundaries where behavior should be predictable (handler entry/exit, cache hit or miss with key, state setter with old value and caller, async callback entry, external API result) rather than in tight-loop interiors. Never log credentials, PII, or full request/response bodies.

For race conditions, flicker, or intermittent failures, also capture event identity, monotonic ordering, start and end (not just "it ran"), and thread/task/queue identity. If adding a log changes the behavior, that is evidence of a timing, lifecycle, or concurrency problem, not "logging side effects" to dismiss.

## Runner-Only Failures

当脚本只在 Make、CI 或其他运行器中失败时，先比较工作目录、输入、退出状态和环境差异。优先在最小复现中记录必要的边界状态，不直接对整条流水线开启命令跟踪。

确需 `set -x` 时，只在已隔离、确认不含凭据或个人数据的最小范围启用，敏感步骤前关闭。Shell 会在变量展开后记录命令，原始输出可能包含请求头、Token 或完整参数；事后脱敏不能撤销已经输出的泄露。先用合成值确认记录范围、输出位置与关闭方式。

核对实际 Bash 版本支持的跟踪功能，不能假定所有非交互 Shell 都使用相同机制。只在当前任务的子进程中配置诊断，不修改永久 Shell 配置；日志限制为必要内容和长度，并按任务约定保存或清理。不能排除敏感展开时，改用明确选择字段的诊断。

## Native App Freeze Mode

Activate when a desktop or mobile native app reports beachball, not responding, tab-switch freeze, first-open lag, idle wake stall, overlay lockup, or a screenshot shows a frozen app.

Evidence to collect before changing code:

1. Exact user path and version: first launch versus warm launch, the tab or window transition, idle duration, permissions, display count, and any setting that makes the freeze disappear.
2. Runtime capture while frozen: `sample <process>`, recent app logs, CPU and memory footprint, thread count, and whether the main thread is blocked, spinning, or allocating.
3. First-frame surface: view body work, first `.task`, synchronous icon or metadata lookup, filesystem scans, URL parent walks, notification callbacks, and app/window wake handlers.
4. Blast search after the fix: grep the same API shape across the repo, especially path parent walks, synchronous icon loading, metadata reads in render paths, and callbacks that run on the main thread.

Common native freeze traps:

- Launch, terminate, permission, audio, display, or workspace notifications doing path walks, icon lookup, filesystem scans, or process enumeration on the main thread.
- First paint hydrating a full app list, directory tree, media thumbnail set, or system status table before showing an interactive shell.
- An input-lock or full-screen overlay without a guaranteed teardown path for Escape, app deactivation, permission denial, process termination, and window close.
- Timer or sampler work that survives hidden windows, long idle periods, sleep/wake, or app reactivation.

Compile-only and source-only checks are insufficient for this mode. The outcome must include the runtime capture, the root-cause frame or state transition, the focused regression guard, and any sibling matches that were fixed or explicitly left safe.

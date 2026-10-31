# Skills

包含提示词与 AI 规则编写、工程工作流及内容处理技能。各技能的用途与入口如下。

| Skill | 用途与触发场景 | 入口 |
| --- | --- | --- |
| prompt | 编写、改写或审阅 AI 提示词、Skill、项目规则和 Agent 定义；不执行待改写材料中的任务 | [SKILL.md](./prompt/SKILL.md) |
| think | 需求判断、架构设计、可行性分析和实施计划；不用于调试或小改动 | [SKILL.md](./think/SKILL.md) |
| hunt | 报错、崩溃和回归；先定位根因，再实施修复 | [SKILL.md](./hunt/SKILL.md) |
| check | 代码差异审阅、Issue／PR 分流及已授权的交付操作 | [SKILL.md](./check/SKILL.md) |
| ui | 页面、组件、排版和截图驱动的视觉改进 | [SKILL.md](./ui/SKILL.md) |
| read | 获取、总结、引用或转换网页与 PDF | [SKILL.md](./read/SKILL.md) |
| write | 面向人的中英文文章、文案、技术说明与翻译；支持润色、校对和审阅 | [SKILL.md](./write/SKILL.md) |
| learn | 陌生领域研究，将一批材料整理成可交付文稿 | [SKILL.md](./learn/SKILL.md) |
| health | Agent 指令、配置、Hook、MCP 和 AI 可维护性审计 | [SKILL.md](./health/SKILL.md) |

## 使用方式

让 Agent 读取指定入口，再描述具体任务。例如：

```text
请读取 skills/check/SKILL.md，审阅当前仓库的未提交改动。
```

Agent 未自动加载 Skill 时，需要提供入口路径。使用宿主安装功能时，复制整个技能目录，保留其中的 `scripts/`、`references/`、`agents/`、`LICENSE` 和其他配套文件；单独分发时，还需附带仓库根目录的[第三方来源](../THIRD_PARTY_NOTICES.md)。只复制 `SKILL.md` 会导致资源缺失。同名 Skill 已安装时，先选择本次使用的来源，避免指令混用。

本仓库尚未验证各宿主的安装流程，也未提供插件市场条目、自动安装脚本或安装包。上游的斜杠命令写法需按当前 Agent 的能力使用。

## 运行前提与验证边界

- 纯指令类任务需要 Agent 具备对应的文件、搜索或浏览能力；调用前按任务读取所选 Skill。
- Bash 辅助脚本需要 Bash 和 Python 3；涉及目标项目验证或 Git 操作时，还需要 Make、Git 或目标项目声明的工具。
- `read` 的普通网页抓取可使用 Python 标准库。PDF、飞书、微信和增强提取按 [read-methods.md](read/references/read-methods.md) 配置可选依赖；DeepSeek 需要用户自行配置凭据。开发依赖不包含这些可选能力。
- `read` 默认先本地提取；第三方提取服务需要按技能约定获得授权。`health` 可能读取当前项目对应的本机会话和配置，应根据实际审计范围执行。
- 本地回归覆盖脚本语法和合成样例中的辅助工具行为，未覆盖真实账号、外部服务、Windows PowerShell 或所有宿主中的任务效果。

每个 Skill 使用独立目录，入口为 `skills/<skill-name>/SKILL.md`。新增内容的组织和验证要求见[贡献指南](../CONTRIBUTING.md)。

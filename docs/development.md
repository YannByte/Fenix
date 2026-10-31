# 开发与交付

本项目用 Python 和 Make 维护仓库 Harness。公开技能位于 `skills/`；项目专属工作流位于 `.agents/skills/`，只服务本仓库，不列入公开技能清单，也不通过本地安装入口分发。

开发依赖按[README](../README.md#本地验证)安装。以下命令从仓库根目录执行；直接运行 `scripts/harness.py` 时，也始终操作脚本所属仓库。

## 盘点

```sh
make scope PYTHON=.venv/bin/python
```

输出分支、HEAD、上游、改动路径和最近提交。包括暂存、未暂存、删除、改名与未跟踪项；特殊文件名保留在 JSON 字符串中。命令不联网、不暂存、不修改 Git 状态；上游信息来自本地引用，不证明远端同步。

## 验证

| 范围 | 命令 | 覆盖 |
| --- | --- | --- |
| 仓库 | `make verify SCOPE=repository PYTHON=.venv/bin/python` | 两类技能元数据、公开清单、Markdown 相对链接、脚本语法和已暂存／未暂存差异空白 |
| 完整 | `make test PYTHON=.venv/bin/python` | 仓库检查与全部回归测试，等同 `make verify SCOPE=full` |

纯文档或规则改动可先用仓库范围；改动脚本、检查器、安装方式或测试时运行完整范围。每个阶段失败即停止，输出已完成阶段；默认每个阶段最多 120 秒、输出上限 1 MiB，超限视为失败。检查器变更需覆盖正常和错误输入。

测试使用隔离目录、合成材料和本机 HTTP 服务，不访问真实账号、会话或外部提取服务。CI 的 `make test` 使用同一入口。静态检查、脚本测试、技能任务效果与宿主加载是不同证据；未验证的部分须明确说明。

## 审阅与提交

先盘点实际工作区，再按用户要求确定审阅基线。逐项检查行为、调用方、输入输出、文档和交付资源；不把盘点或校验通过当作审阅。工作流入口见[仓库规则](../AGENTS.md#按任务读取)。

提交只包含已授权任务的具体文件，保留其他工作和部分暂存。提交前核对 HEAD、暂存差异及敏感信息；HEAD 或范围意外变化时停止。使用项目已有的提交信息约定，不自动创建版本、Tag 或变更日志。推送需明确授权，推送前核对远端和分支，完成后核对远端提交及 CI；不自动强推或改写历史。

## 本地安装

```sh
make install-plan PYTHON=.venv/bin/python
make install-local PYTHON=.venv/bin/python
```

第一条只预览，第二条安装。目标默认为 `$CODEX_HOME/skills`，未设置时为 `~/.codex/skills`。可用以下入口指定隔离验收目录或其他本地目标：

```sh
.venv/bin/python scripts/harness.py install --dest /tmp/fenix-skills
.venv/bin/python scripts/harness.py install --dest /tmp/fenix-skills --apply
```

只链接已通过元数据和相对链接检查的公开技能。链接指向同一来源时保持原样；同名目录、其他来源或失效链接视为冲突，任何冲突都会在写入前终止。中途失败或中断时，只回收本次创建且仍指向本次来源的链接，保留原有内容。命令不会卸载旧技能或修改宿主配置。

保留仓库当前位置，确保资源、许可证及[来源列表](../THIRD_PARTY_NOTICES.md)持续可达；源码改动会直接反映到本地技能。安装后仍需核对资源可达性，宿主加载与任务效果另行验收。该入口提供本地链接安装，不生成插件、安装包或远端发布。

# Fenix

**火凤凰 · Yann 的开源 AI Agent Skill 库。**

把日常工作中可复用的方法整理成 Skill，逐步积累、验证和改进。

技能覆盖提示词与 AI 规则编写、规划、调试、审阅、产品设计、阅读、写作、研究和 Agent 健康检查。使用入口和运行前提见[技能清单](skills/README.md)；添加内容时查看[收录范围](SCOPE.md)和[贡献指南](CONTRIBUTING.md)。

## 目录结构

```text
Fenix/
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── VERSION
├── Makefile
├── .agents/skills/
├── assets/skill-template/
├── docs/
├── scripts/
├── tests/
└── skills/
    └── README.md
```

每个 Skill 使用独立目录，以 `SKILL.md` 说明用途、触发条件和执行步骤；需要时附带脚本、参考资料或模板。

## 获取仓库

```sh
git clone https://github.com/YannByte/Fenix.git
```

具体使用方式由每个 Skill 自己说明，通用入口见[技能清单](skills/README.md#使用方式)。目前提供技能源文件，尚未发布插件或安装包。

## 本地验证

开发检查需要 Python 3.9 或更高版本和 Make：

```sh
cd Fenix
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
make test PYTHON=.venv/bin/python
```

检查覆盖 Skill 元数据、技能清单入口、Markdown 相对链接、Python／Bash 脚本语法，以及检查器和辅助脚本的回归测试。脚本行为使用临时目录、合成材料和本机 HTTP 服务验证，不调用真实账号或外部提取服务。网络链接、Markdown 锚点、Windows PowerShell、宿主兼容性和完整任务效果仍需按实际场景另行验证。推送到 `main` 或提交 Pull Request 时，GitHub Actions 运行相同检查。

仓库 Harness 的改动盘点、分层验证、审阅提交和本地安装入口见[开发与交付](docs/development.md)。项目工作流保留在 `.agents/skills/`，与公开分发的技能分开维护。

仓库版本统一维护在 [VERSION](VERSION)，当前为开发版本，尚未发布。

## 许可证

[MIT](LICENSE)。第三方内容保留各自的许可证与署名，详见[第三方来源](THIRD_PARTY_NOTICES.md)。单独分发 Skill 时，需附带该来源文档并保留技能目录内的许可证及附加声明。

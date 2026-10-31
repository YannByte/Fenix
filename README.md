# Fenix

**火凤凰 · Yann 的开源 AI Agent Skill 库。**

把日常工作中可复用的方法整理成 Skill，逐步积累、验证和改进。

首批 Skill 尚未收录。先查看[技能清单](skills/README.md)和[收录范围](SCOPE.md)；添加内容时使用[贡献指南](CONTRIBUTING.md)。

## 目录结构

```text
Fenix/
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── VERSION
├── Makefile
├── assets/skill-template/
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

具体使用方式由每个 Skill 自己说明。目前没有可安装的 Skill、插件或安装包。

## 本地验证

开发检查需要 Python 3.9 或更高版本和 Make：

```sh
cd Fenix
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
make test PYTHON=.venv/bin/python
```

检查覆盖 Skill 元数据、技能清单入口、Markdown 相对链接、Python 脚本语法和检查器回归测试。检查不执行 Skill 内的脚本，也不验证网络链接、Markdown 锚点、宿主兼容性或任务效果；这些内容按 Skill 的实际场景另行验证。推送到 `main` 或提交 Pull Request 时，GitHub Actions 运行相同检查。

仓库版本统一维护在 [VERSION](VERSION)，当前为开发版本，尚未发布。仓库组织参考 [Waza](https://github.com/tw93/Waza)，详见[第三方来源](THIRD_PARTY_NOTICES.md)。

## 许可证

[MIT](LICENSE)。引用或改编的第三方内容按其标注的许可证与署名要求处理。

# 第三方来源

## Waza

Fenix 的仓库组织与开发检查入口参考 [Tw93/Waza](https://github.com/tw93/Waza/tree/df1ef2390e89d70dee07f928ac09aa7ba4b90299)。首批八个 Skill 也收录自该仓库，基线为 `3.41.0`，完整提交为 `df1ef2390e89d70dee07f928ac09aa7ba4b90299`。

收录路径为 `skills/{think,hunt,check,ui,read,write,learn,health}/`，包含对应的指令、参考文件、辅助脚本和专家审阅材料。八个目录内分别保留 Waza 的 MIT 许可证全文和 `NOTICE`，版权为 `Copyright (c) 2026 Tw93`，便于单独分发。

Fenix 对八个 `SKILL.md` 的改动限于 frontmatter：把 `when_to_use` 与 `dispatch_intent` 移入标准 `metadata`，并增加 `license` 和上游来源字段。技能正文和配套文件保持基线内容；未引入上游品牌素材、插件市场配置、安装器、全局规则或自动更新机制。上游 `skills/RESOLVER.md` 未收录，本仓库使用[技能清单](skills/README.md)作为入口。

`tests/waza_read_fetch_smoke.py` 收录自上游 `tests/read_fetch_smoke.py`，内容保持不变，许可证见 [tests/LICENSE.waza](tests/LICENSE.waza)。其余 Fenix 文档、模板和验证代码按本仓库需要维护。

### UI 技能的附加来源

`ui/references/design-reference.md` 保留了上游对以下项目的署名：

- [pbakaus/impeccable](https://github.com/pbakaus/impeccable)：部分设计规则的改编来源，Apache-2.0。许可证及原版权声明随 [ui 技能](skills/ui/licenses/impeccable-Apache-2.0.txt)分发。
- [getdesign.md](https://getdesign.md)／[VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)：DESIGN.md 模板的改编来源，MIT；概念署名 Google Stitch。许可证随 [ui 技能](skills/ui/licenses/awesome-design-md-MIT.txt)分发。
- [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)：内容真实性、卡片对齐和策略性省略的灵感来源。

`write/references/write-technical.md` 中对 ASD-STE100 和相关写作材料的来源、适用边界与非认证声明也按上游保留。后续改编第三方内容时，须保留适用的版权、许可证和变更声明。

## Agent Skills

Skill 元数据和目录结构参照 [Agent Skills 规范](https://agentskills.io/specification)。本仓库检查名称、描述和目录一致性；触发质量、任务效果与宿主安装兼容性仍需实际验证。

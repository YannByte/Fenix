# 第三方来源与变更声明

本文集中记录参考来源、上游基线、版权署名和本仓库的改动范围。单独分发技能或参考文件时，须附带本文及对应许可证；许可证原文中的版权声明保持不变。

## Waza

Fenix 的仓库组织、开发检查入口和首批八个 Skill 参考或收录自 [Tw93/Waza](https://github.com/tw93/Waza/tree/df1ef2390e89d70dee07f928ac09aa7ba4b90299)。基线版本为 `3.41.0`，完整提交为 `df1ef2390e89d70dee07f928ac09aa7ba4b90299`。

收录路径为 `skills/{think,hunt,check,ui,read,write,learn,health}/`，包含对应的指令、参考文件、辅助脚本和专家审阅材料。版权为 `Copyright (c) 2026 Tw93`；八个技能目录各自保留 MIT 许可证全文，便于单独分发。

相对于基线，Fenix 做了以下调整：

- 将入口 frontmatter 中的 `when_to_use` 与 `dispatch_intent` 移入标准 `metadata`，增加本地 `license` 引用。
- 移除入口中的上游来源字段、正文中的上游品牌自称和强制 `🥷` 输出要求，改用通用的技能名称和错误提示。
- 将分散的来源介绍与致谢集中到本文，删除本仓库此前添加的八份 `NOTICE`；许可证和必要的文件变更标记继续保留。
- 将辅助脚本中的临时目录名、测试文件名及内部 Python 探测标识改为通用名称；清理当前脚本未使用的旧品牌环境变量清理项，其余路径和执行环境保护逻辑保留。
- 将安装目录说明改为单技能目录或集合根目录，移除对上游发行包形态的专属表述。

`tests/read_fetch_smoke.py` 收录自同一提交下的 `tests/read_fetch_smoke.py`，只调整了临时目录前缀；许可证见 [tests/LICENSE.third-party](tests/LICENSE.third-party)。未引入上游品牌素材、插件市场配置、安装器、全局规则或自动更新机制；未收录上游 `skills/RESOLVER.md`。

## UI 技能的附加来源

`skills/ui/references/design-reference.md` 中的以下材料经 Waza 改编后收录：

- [pbakaus/impeccable](https://github.com/pbakaus/impeccable)：Reflex Fonts、Font Selection、OKLCH、Theme Matrix、Absolute Bans、motion rules 和 AI Slop Test 的改编来源。版权为 `Copyright 2025 Paul Bakaus`，使用 Apache-2.0；许可证全文及原版权声明见 [Apache-2.0.txt](skills/ui/licenses/Apache-2.0.txt)。
- [getdesign.md](https://getdesign.md)／[VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)：DESIGN.md Scaffold 的改编来源，版权为 `Copyright (c) 2026 VoltAgent`，使用 MIT；许可证见 [design-template-MIT.txt](skills/ui/licenses/design-template-MIT.txt)。DESIGN.md 概念署名 Google Stitch。
- [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)：Content Authenticity、Multi-Card Alignment 和 Strategic Omissions 的灵感来源。

本仓库调整了该参考文件中的项目介绍和署名位置，保留设计规则及实际工具命令；文件中保留变更标记并链接到本文。上述附加许可证须随对应内容一起分发。

## 阅读辅助脚本的灵感来源

[joeseesun/qiaomu-markdown-proxy](https://github.com/joeseesun/qiaomu-markdown-proxy) 是上游 `read` 辅助脚本所注明的灵感来源：`fetch.sh` 借鉴其提取服务回退思路，`fetch_feishu.py` 借鉴其飞书 API 集成与文档解析思路，`fetch_weixin.py` 借鉴其基于 Playwright 的微信文章提取思路。原脚本中的致谢集中保留于本文。

## 技术写作参考

`skills/write/references/write-technical.md` 的上游说明注明，其原创改编参考了 [asd-ste100-skill 的写作规则摘要](https://github.com/danyuchn/asd-ste100-skill/blob/master/references/writing-rules.md)及[适用范围与事实保留说明](https://github.com/danyuchn/asd-ste100-skill/blob/master/SKILL.md)。该指南采用部分清晰表达原则，不包含获批词典，也不构成 ASD-STE100 合规认证。本仓库将来源介绍移至本文，正文继续保留适用边界与非认证声明。

## Agent Skills

Skill 元数据和目录结构参照 [Agent Skills 规范](https://agentskills.io/specification)。本仓库检查名称、描述和目录一致性；触发质量、任务效果与宿主安装兼容性仍需实际验证。

---
name: video-generation
description: 生成和修订视频片段时使用，作为独立工种参与本工程协作。
---

# 视频生成

读取根目录 README.md，按 skills/task-management/SKILL.md 管理本次工作，按 skills/asset-management/SKILL.md 交付正式资产。

记录模型、提示词、参考资产、动作、时长与画幅，检查连续性。

使用本地 ComfyUI 时先读 platform/comfyui/README.md。只通过 client.mjs 的 HTTP 接口使用已有桌面版，不安装另一套 ComfyUI、不修改其源码或 Python 环境。调试资产用 sync-assets；批量优先复用 workflows 下已登记的 API 图和 definition，通过 parameters 与 {"asset":"assets/..."} 引用图片，使用 run 等待并收集结果。升级后先单任务回归；保留任务图、资产哈希和服务版本记录。视频/音频输入必须按工作流节点实际接口接入，不假定图片上传接口通用。

按具体需求检索可用输入与版本；缺失时记录缺口，按授权补充或提出依赖任务。可独立开展、并行协作或根据反馈返工，不要求其他工种整体先完成。

要求、流程、过程文件与候选结果留在 tasks/<task-id>/，正式采用的交付物进入 assets/clips/。

# 项目 Agent 指南

项目技能位于 ".agents/skills/<skill-name>/SKILL.md"，执行相关任务时读取对应技能。全部路径以项目根目录为基准，先阅读 README.md 了解资产与任务结构。

技能统一描述以下内容：产物与用途、输入与依赖、生产软件、制作流程、格式与验收、存放与归档。新增或更新技能时保留 YAML frontmatter 中的 name 和 description；名称使用小写字母、数字和连字符，description 说明实际能力与适用任务。

技能用于说明产物如何制作与交付；实际任务的目标、参数、执行日志和候选结果放在 tasks/，正式采用资产放在 assets/，软件调用接口放在 platform/。不把单次任务记录写进通用技能。

按任务类型使用 storytelling、scripting、art-style、character-design、scene-design 或 storyboarding；任务档案与正式交付分别参考 task-management、asset-management。Blender 任务使用 tasks/blender/<task-id>/。

目录路径和定稿入库按 README.md 与 DIRECTORY.md 执行。新任务放在 tasks/<主工具>/<task-id>/，旧任务按 tasks/README.md 查找。assets/ 中每项资产只保留供后续流程使用的当前定稿，历史版本保留在任务档案。

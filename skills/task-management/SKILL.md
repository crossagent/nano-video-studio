---
name: task-management
description: 管理本工程生成、剪辑及创作任务，保存要求、流程、执行记录和过程产物。
---

# 任务管理

读取工程根目录 README.md，每项任务使用 tasks/<task-id>/。

在 task.md 记录工种、类型、状态、目标、要求、输入资产路径及版本、交付位置、验收标准和实际依赖。workflow.md 保存步骤、工具、提示词、参数或剪辑方案。log.md 保存执行、失败、重试与评审。

专用参考放 inputs，草稿和工程文件放 work，生成结果与候选导出放 output。遵循用户已有授权，不因目录规则增加审批。

现有 MCP 生成任务取得数据库 ID 后，使用 tasks/task-<id>/ 保存上述材料。数据库 completed 只表示执行完成，验收与入库另记。正式采用后将文件复制到 assets 对应类型目录，保留任务原始结果并记录目标路径与版本。

状态可用 planned、running、review、completed、failed、cancelled。任务以实际输入依赖协调工种，允许并行、返工和双向迭代，不建立统一阶段顺序。

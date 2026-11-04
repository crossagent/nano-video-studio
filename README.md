# nano-video-studio

工程按资产与任务管理。创作由不同工种协作完成，不设置编号阶段或默认执行顺序。

## 目录

- assets/scripts/：故事大纲、剧本。
- assets/settings/style/：美术风格设定。
- assets/settings/characters/：角色设定集。
- assets/settings/scenes/：场景设定集。
- assets/storyboards/：分镜表、分镜图。
- assets/clips/：正式采用的视频片段。
- assets/audio/：配音、音乐、音效。
- assets/edits/：成片、字幕、封面。
- tasks/<task-id>/：具体工作的要求、流程、记录与过程产物。
- skills/：资产管理、任务管理及各工种能力。
- platform/：ComfyUI 的资产同步、工作流与批量执行接口。

## 资产

资产是正式采用的产物，按类型管理，不按制作步骤管理。每项资产应有说明（文档本身或同名 .md），记录用途、版本、来源任务及关联资产。

草稿、候选结果、失败产物和剪辑工程留在任务目录。产物通过该任务的验收标准后，将采用版本复制到资产目录，保留来源关系。任务执行完成不自动等于资产入库。

## 任务

每项工作使用独立目录 tasks/<task-id>/：

- task.md：ID、工种、任务类型、状态、目标、要求、输入资产及版本、交付位置、验收标准和实际依赖。
- workflow.md：本任务的执行方案、工具、模型、提示词、参数，或剪辑时间线与音画方案。
- log.md：执行、失败、重试、评审及最终资产去向。
- inputs/：任务专用参考或输入快照。
- work/：草稿、工程文件、时间线及中间文件。
- output/：生成结果、候选导出。

任务使用唯一且有意义的 ID，例如 video-shot-001、edit-trailer-001。ComfyUI 批量任务使用批次清单中指定的 ID，结果写入对应 output/，同时保存要求、工作流、执行记录与输出清单。

## 工种协作

故事创作、编剧、美术、角色设计、场景设计、分镜、视频生成、剪辑是不同工种，均可独立接单、并行工作和反复修订。上下游由具体任务引用的输入与交付确定，不由工种编号确定。输入不足时记录缺口，按当前授权补充或创建相关任务，不要求先完成整套其他工作。

变更已被引用的资产时记录版本，并标记受影响任务需要复核；不静默覆盖仍被引用的版本。

文本规则、资产说明、任务要求与记录纳入 Git；媒体文件及任务过程文件默认留在本地。

## 平台能力

platform/ 保存通用生成平台接入。当前通过本地 ComfyUI 提供生图和生视频：图形界面调试工作流，Codex 直接调用 API 批量执行。安装与模型独立维护，详见 [平台说明](platform/README.md)。

nano-agent 与 ComfyUI 仅通过 HTTP 交换图片快照、工作流和结果。调试时运行 `node platform/comfyui/client.mjs sync-assets` 导入资产；工作流验收后导出 API 图并登记命名参数，批量时运行 `node platform/comfyui/client.mjs run <批次.json>`。具体约定和 MiniMax 示例见 [接入说明](platform/comfyui/README.md)。

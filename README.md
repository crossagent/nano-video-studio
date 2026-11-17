# nano-video-studio

工程按资产与任务管理。`project/<项目名>/` 分别保存各创作项目的小说、资产和任务；当前项目为 `project/starcraft/`。`platform/` 和技能由各项目共享。影视创作由不同工种协作完成，不设置编号阶段或固定顺序。

## 目录结构

目录边界、定稿入库和第一幕试点见[目录与归档规则](DIRECTORY.md)。现有任务可从[工具索引](project/starcraft/tasks/README.md)查找。

- `project/starcraft/novels/`：原著小说资源与参考文件。
- `project/starcraft/assets/scripts/`：采用的故事大纲、梗概、分场大纲与电影文学剧本。
- `project/starcraft/assets/settings/style/`：影视美术风格与视觉规范。
- `project/starcraft/assets/settings/characters/`：核心角色设定集与设计图。
- `project/starcraft/assets/settings/scenes/`：场景设定集、空间与光影基准。
- `project/starcraft/assets/storyboards/`：逐镜分镜脚本、分镜图、Blender 3D 预演工程与视口渲染。
- `project/starcraft/assets/clips/`：正式采用的动态与视频片段。
- `project/starcraft/assets/audio/`：配音、配乐、音效素材。
- `project/starcraft/assets/edits/`：采用的剪辑工程、时间线与交付导出。
- `project/starcraft/tasks/`：按主工具组织的制作任务、专用脚本、工作流和候选结果。
- `platform/`：共享软件接口、运行器和可复用工作流模板。
- `.agents/skills/`：资产管理、任务管理及各专业工种技能库。

## 资产管理规范

`project/starcraft/assets/` 是下游取用的正式资产库。每项资产只留当前定稿，采用结论须明确到具体文件及用途。
每项资产均配有说明文档（同名 `.md` 或专用规格），记录用途、版本、来源任务及关联资产：
- 角色设定保留视觉锚点、服装细节与色板 Hex；
- 场景设定保留空间关系、摄影构图与光影基准；
- 分镜记录镜号 ID、时长、景别、运动、画面及 3D Previs 调度。

草稿、过程文件、候选导出和历史定稿留在任务档案。只有确定供后续流程使用的文件才复制入库。替换定稿时先确认旧版可从任务档案恢复，再更新正式资产和清单。

Git 保存目录 README、规格、任务档案和可共享工作流。生成的图像、视频、音频及制作工程保存在本机或独立存储。克隆仓库后，按资产说明恢复实际媒体。

## 任务执行规范

任务使用独立目录 `project/starcraft/tasks/<主工具>/<task-id>/`，例如 `project/starcraft/tasks/blender/<task-id>/`。纯文本创作归 `project/starcraft/tasks/writing/`。现有任务按[工具索引](project/starcraft/tasks/README.md)查找。

- `task.md`：任务目标、要求、主工具及辅助工具、输入资产路径及版本、验收标准与依赖。
- `workflow.md`：本任务的执行步骤、工具、参数或预演方案。
- `log.md`：执行过程记录、重试日志、评审结论与资产去向。
- `inputs/`：任务专用参考。
- `work/`：工程文件、草稿与中间文件。
- `output/`：生成结果与候选导出。

## 专业工种协同

故事创作、编剧、美术风格、角色设计、场景设计、分镜（含 3D 预演）作为核心工种，均可独立接单、并行工作并双向迭代。

## CapCut 桌面剪辑

使用本机 CapCut 国际版和 `capcut_local` stdio MCP 操作本地草稿，不使用 CapCut Web 或云端草稿。服务代码及上游说明位于 `platform/capcut-local/`；本机草稿目录为 `D:/CapCut Drafts`。调用前确认草稿版本和锁定状态，先备份，关闭目标草稿后再写入，并在桌面版重新打开验证。文字等素材可能需要已有草稿模板；MCP 的本地列表可用不代表所有剪辑和导出能力已验证。

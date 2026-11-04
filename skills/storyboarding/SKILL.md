---
name: storyboarding
description: 设计分镜剧本、镜头构图、运动调度及 3D Previs（粗模预演）时使用，作为独立工种参与本工程协作。
---

# 分镜与 3D 预演

读取工程根目录 README.md，按 skills/task-management/SKILL.md 管理工作，按 skills/asset-management/SKILL.md 交付正式资产。

## 工作规范
1. **分镜脚本（2D）**：
   - 记录镜号 ID、景别（ELS/FS/MS/MCU/CU/ECU）、时长、摄影机运镜方式、画面动作描写、角色调度及对白。
   - 正式分镜脚本归档至 `assets/storyboards/`。
2. **3D 分镜预演与相机调度（3D Previs）**：
   - **平台层调用**：所有 3D 引擎与自动化脚本调用统一交由 `platform/blender/` 管理（通过 `platform/blender/run.cmd` 执行，利用 `previs_toolkit.py` 统一步骤与画幅）。
   - **任务目录规约**：每一次具体的 3D 建模、粗模搭建、相机运动与灯光预演任务，均在 `tasks/blender/<task-id>/` 下独立开展与记录。
   - **资产归档**：验收通过的正式 `.blend` 工程文件与快照渲染图，归档至 `assets/storyboards/`。

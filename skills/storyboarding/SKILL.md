---
name: storyboarding
description: 使用 Blender 制作白模分镜预演（3D Previs）、设计镜头构图与运动调度，支持人机协同迭代。
---

# 分镜与 3D 白模预演 (Storyboarding & 3D Previs)

读取工程根目录 `README.md`，按 `skills/task-management/SKILL.md` 管理具体任务，按 `skills/asset-management/SKILL.md` 交付正式资产。

---

## 核心工作流准则

### 1. 用 Blender 生成白模分镜
* **白模预演（White-Box / Blocking）**：在分镜设计阶段，必须使用 Blender 3D 引擎，通过基础几何体（立方体、圆柱、阶梯金字塔、地形块等白模/灰模）与标准材质色块快速搭建场景与角色体量关系；
* **相机调度与画幅标准**：精确架设各镜头的摄影机位置、焦距（毫米数）、俯仰摇移轨迹，统一采用 2.39:1 变形宽银幕（1920x804）或指定画幅；
* **平台统一调用**：统一通过 `platform/blender/run.cmd` 调用执行，复用 `platform/blender/previs_toolkit.py` 提供的构图与视口渲染工具。

### 2. 过程文件放在 task 中，方便人类参与迭代修改
* **独立任务目录**：每一次具体的 Blender 分镜任务，必须且只能存放在 `tasks/blender/<task-id>/` 目录下；
* **人机协同透明度**：
  * 场景构建脚本（`scene_build.py` 或 `build_previs.py`）、中间工程草稿（`work/*.blend`）、临时视口渲染图（`output/*.png`）及调试日志（`log.md`）全部留在该 task 目录内；
  * 便于人类创作者随时直接在桌面端 Blender GUI 中打开 `.blend` 工程，交互式调整摄影机机位、焦段、灯光或模型位置，完成双向迭代。

### 3. 成品必须经人类确认后，方可入库 asset 目录
* **严禁自动擅自入库**：工具生成或脚本跑通仅代表任务生成结束，**绝不自动等同于资产入库**；
* **人类验收闭环（Human-in-the-Loop）**：生成完各机位快照与初步工程后，状态置为 `review`，等待人类导演/制作人确认；
* **正式归档**：只有在人类明确确认并验收通过后，才将最终定稿的 `.blend` 工程与分镜成图复制到 `assets/storyboards/` 正式资产库中，并在 `log.md` 记录验收结论与目标版本。

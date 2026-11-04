---
name: storyboarding
description: 使用 Blender 制作 3D 白模动态分镜视频（Previs Video / 3D Animatic）、设计镜头构图与连续运动调度，支持人机协同迭代。
---

# 分镜与 3D 白模视频预演 (Storyboarding & 3D Previs Video)

读取工程根目录 `README.md`，按 `.agents/skills/task-management/SKILL.md` 管理具体任务，按 `.agents/skills/asset-management/SKILL.md` 交付正式资产。


## 产物与用途

制作连续 3D 白模预演视频、可编辑 Blender 工程和镜头清单，用于检验构图、空间、动作、运镜与剪辑节奏，支持人机协同修改。

## 输入与依赖

读取剧本、相关角色和场景设定及其版本，明确镜头范围与验收标准。缺失输入记录在任务中，按实际依赖推进。

## 生产软件

使用 Blender 搭建白模、制作动画并保存工程，使用 FFmpeg / H.264 导出视频。调用前读取项目根目录 platform/blender/README.md，统一使用 platform/blender/run.cmd 和 platform/blender/previs_toolkit.py。

## 制作流程



### 1. 用 Blender 生成 3D 白模动态分镜视频（非静态单图）
* **最终产物是连续视频**：3D 白模分镜的最终交付物必须是 **3D 预演视频（Previs Video / 3D Animatic，H.264 MP4 格式）**，而不是零散的静态分镜图片；
* **白模体量搭建（White-Box / Blocking）**：在 Blender 3D 引擎中，使用基础几何体（立方体、圆柱、阶梯金字塔、地形块等白模/灰模）与标准材质色块搭建场景空间与角色体量关系；
* **多镜头时间轴绑定与动画**：
  * 利用 Blender 时间轴标记（Timeline Camera Markers）将多个镜头的摄像机按时间顺序串联绑定；
  * 包含摄像机运镜（推、拉、摇、移、跟、俯冲）、主体位移动态、环境动态（闪电、雷达转动、地震剧烈晃动、信标发射等）以及各镜头的剪辑节奏与时长；
* **画幅与编码标准**：统一采用 2.39:1 变形宽银幕（1920x804）、24 fps、FFmpeg / H.264 编码导出 MP4 视频；
* **平台统一调用**：底层统一通过 `platform/blender/run.cmd` 调度执行，复用 `platform/blender/previs_toolkit.py` 预置工具。

### 2. 过程文件放在 task 中，方便人类参与迭代修改
* **独立任务目录**：每一次具体的 Blender 分镜任务，必须且只能存放在 `tasks/blender/<task-id>/` 目录下；
* **人机协同透明度**：
  * 场景构建与动画脚本（`build_previs_video.py`）、中间工程文件（`work/*.blend`）、预演导出视频（`output/*.mp4`）及调试日志（`log.md`）全部保留在该 task 目录内；
  * 便于人类创作者随时直接在桌面端 Blender GUI 中打开 `.blend` 工程，拖动时间轴检查相机与动画，手动交互式微调关键帧、焦段、构图与时长，完成人机双向迭代。

### 3. 成品必须经人类确认后，方可入库 asset 目录
* **严禁自动擅自入库**：自动化脚本生成出视频仅代表任务完成初步渲染，**绝不自动等同于资产入库**；
* **人类验收闭环（Human-in-the-Loop）**：生成预演视频后，任务状态置为 `review`，等待人类导演/制作人确认；
* **正式归档**：只有在人类明确确认并验收通过后，才将最终定稿的 Previs 视频与 `.blend` 工程归档到 `assets/storyboards/` 正式资产库中，并在 `log.md` 记录验收结论与目标版本。

## 格式与验收

交付 H.264 MP4 连续预演视频、.blend 工程和 UTF-8 Markdown 镜头清单，画面为 1920×804（约 2.39:1）、24 fps。镜头清单记录镜头 ID、时长、景别、运动、构图和引用资产。静态 PNG 只作检查辅助。

打开工程检查时间轴相机绑定与关键帧，播放视频核对镜头顺序、时长、运动连续性和导出参数；记录问题与人类验收结论。

## 存放与归档

路径相对项目根目录：任务文件统一放 tasks/blender/<task-id>/，工程放 work/，候选视频放 output/，脚本与 task.md、workflow.md、log.md 放任务根目录。人类明确验收通过后，将定稿视频、工程与镜头清单复制到 assets/storyboards/，记录版本、用途和来源任务，保留原始结果。

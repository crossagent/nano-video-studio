# 任务名称：第一幕（Act 1）Blender 3D 粗模分镜预演（Previs / Blocking）

- **任务目录**：`tasks/blender/previs-blocking-act-001/`
- **平台支持**：`platform/blender/`（Blender 5.2.3 LTS）
- **状态**：`completed`

## 任务目标
通过极简低模/几何体（方块、简易地形、金字塔、圆柱体等）快速搭建第一幕核心场景与道具的空间体量关系，并根据分镜脚本（Shot 01 ~ Shot 20）架设摄影机机位与调度，输出可交互的 `.blend` 工程文件及各镜头分镜预演静帧。

## 场景与道具资产体量规划（Primitives）
1. **地貌 1：贝卡·罗麦浪与山脊**（起伏平原 + 简易低模山体）
2. **载具：樱桃红多功能联合收割机**（主方块车身 + 侧边履带块 + 驾驶舱方块 + 前置收割滚筒）
3. **地标：自由避难所防风圈与旧式防空导弹塔**（八边形土堤 + 双联装导弹发射方块与雷达圆盘 + 预制半圆柱穹顶板房）
4. **地貌 2：萨尔那加出土神庙裂谷**（两面高耸峡谷断崖 + 阶梯金字塔巨构 + 贯穿天际的纯能圆柱/圆锥光柱）
5. **地貌 3：查尔星熔岩废土**（熔岩断裂地面 + 异虫几丁质尖塔椎体）

## 摄影机调度（Camera Blocking）
- 按照分镜脚本参数精确设置镜头焦距（16mm、24mm、35mm、50mm、85mm 等）；
- 配置 2.39:1 宽银幕画面构图（1920x804）；
- 分别建立 Shot 01, Shot 02, Shot 03, Shot 05, Shot 07, Shot 09, Shot 12, Shot 15, Shot 17, Shot 19 对应机位。

## 交付资产
- 工程文件：`assets/storyboards/previs_act01_blocking.blend`
- 视口渲染：`assets/storyboards/previs_renders/*.png`
- 评审报告：`act01_previs_report.md`

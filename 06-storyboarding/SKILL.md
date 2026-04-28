---
name: "video-storyboarding"
description: "将剧本转化为可视化的分镜表。当需要规划镜头语言、相机运动或确定视频节奏时调用。触发词：'画分镜'、'分镜脚本'、'镜头规划'。"
---

# 脚本分镜 (Video Storyboarding)

## 1. 技能描述
本技能是视频生产的“施工蓝图”，明确每个镜头的景别、构图、相机运动和持续时间。

## 2. 使用时机
- 在剧本、角色和场景设定全部完成后。

## 3. 执行指令
1. **镜头拆解**：将剧本细分为具体的镜头（Shot）。
2. **镜头语言规划**：定义景别、构图和相机运动。
3. **视觉 Prompt 合成**：整合剧本描述、风格后缀和角色锚点。

## 4. 交付物与存放位置
- **分镜表 (JSON)**: `06-storyboarding/storyboard.json`
- **分镜预览 (Markdown)**: `06-storyboarding/storyboard_preview.md`

## 5. 约束 with 规范
- 必须使用标准的影视工业术语。
- 交付物必须严格存放在 `06-storyboarding/` 目录下。

## 6. 示例
```json
[
  {
    "shot_id": "S01_01",
    "shot_type": "Extreme Close-up",
    "camera_movement": "Static",
    "visual_prompt": "Extreme close-up of Emilia's blue eye...",
    "duration": 2
  }
]
```

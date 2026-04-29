---
name: "video-scripting"
description: "负责视频剧本的深度创作与结构化拆解。当需要将创意转化为包含旁白、视觉描述和精确时长预估的脚本时调用。触发词：'写剧本'、'拆解故事'、'视频大纲'。"
---

# 视频脚本编写 (Video Scripting)

## 1. 技能描述
本技能旨在将原始创意或文本素材转化为机器可理解、流程可执行的结构化剧本。

## 2. 使用时机
- 在故事大纲（来自 01-storytelling）定稿后，需要将其转化为具体脚本时。

## 3. 执行指令
1. **故事大纲分析**：读取 `skills/01-storytelling/story_outline.json`，识别核心情节。
2. **旁白创作**：编写口语化、有节奏感的旁白（VO）。
3. **结构化拆解**：将剧本拆分为多个场景（Scene）。

## 4. 交付物与存放位置
- **结构化剧本 (JSON)**: `[project]/assets/02-scripting/script.json` (包含旁白、视觉描述、时长)
- **剧本预览 (Markdown)**: `[project]/assets/02-scripting/script_preview.md`

## 5. 约束与规范
- 视觉描述必须包含主体、动作、环境。
- 交付物必须严格存放在 `[project]/assets/02-scripting/` 目录下。

## 6. 示例
```json
[
  {
    "scene_id": 1,
    "voiceover": "在科技与自然交织的未来...",
    "visual_description": "一座充满绿植的未来主义城市",
    "duration": 5
  }
]
```

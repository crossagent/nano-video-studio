---
name: "video-storyboarding"
description: "将剧本转化为可视化的分镜表。当需要规划镜头语言、相机运动或确定视频节奏时调用。触发词：'画分镜'、'分镜脚本'、'镜头规划'。"
---

# 脚本分镜 (Video Storyboarding)

## 1. 技能描述
本技能是视频生产的“施工蓝图”，明确每个镜头的景别、构图、相机运动和持续时间。

## 2. 使用时机
- 在剧本、角色和场景设定全部完成后。

## 3. **执行指令**
1. **资源整合与检索**：
   - **必须**在执行前检索 `03-art-style/style_guide.md`、`04-character-design/characters/[name]/character_guide.md` 和 `05-scene-design/scenes/[scene]/scene_guide.md`。
   - 提取其中的核心设计点、视觉锚点和资产路径，确保分镜描述与之完全一致。
2. **镜头拆解**：将剧本细分为具体的镜头（Shot）。
3. **镜头语言规划**：定义景别、构图和相机运动。
4. **分镜预览生成 (Markdown Preview)**：
   - 编写 `[project]/assets/06-storyboarding/storyboard_preview.md`。
   - **必须包含**：每个镜头的详细描述、关联的角色参考图、场景参考图及艺术风格说明。
5. **生成任务流 (Generation Workflow)**：
    - **创建提案 (Propose)**：
      根据 `storyboard_preview.md` 的描述，为每个 Shot 提交生图提案。
      - **模型表**：推荐 `model_openrouter_gpt54_image`。
      - **参数**：必须关联角色设定图和场景图。
    - **获取审批**：向用户展示分镜提案列表及 ID。
    - **触发执行 (Execute)**：
      审批通过后，调用 `run_task.py` 生成分镜关键帧。

## 4. 交付物与存放位置
- **分镜预览与详细描述 (Markdown)**: `[project]/assets/06-storyboarding/storyboard_preview.md`
- **分镜关键帧目录**: `[project]/assets/06-storyboarding/shots/`
- **关键帧图片**: `[shot_id].png` (如 S01_01.png)

## 5. 约束与规范
- 必须使用标准的影视工业术语。
- **分镜描述必须基于 03、04、05 的 Markdown 文档内容**，严禁出现视觉矛盾。
- 交付物必须严格存放在 `[project]/assets/06-storyboarding/` 目录下。

## 6. 示例 (storyboard_preview.md 片段)
### 镜头 S01_01
- **景别**: 特写 (Close-up)
- **相机运动**: 固定 (Static)
- **详细描述**: 镜头对准艾米利亚的脸部，她正专注地看着实验台。背景中隐约可见“遗忘实验室”中心培养皿发出的冷蓝色光芒。
- **资源关联**:
  - 角色：`[project]/assets/04-character-design/characters/Emilia/character_sheet.png`
  - 场景：`[project]/assets/05-scene-design/scenes/ForgotLab/concept.png`
  - 风格：`[project]/assets/03-art-style/style_guide.md` (设计点：高对比度冷暖光)

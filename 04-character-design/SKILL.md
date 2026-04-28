---
name: "video-character-design"
description: "负责视频角色的视觉设定与一致性维护。当需要设计角色形象、生成三视图、表情特写或准备 AI 角色一致性素材时调用。触发词：'设计角色'、'角色设定'、'角色一致性'。"
---

# 角色设定 (Video Character Design)

## 1. 技能描述
本技能负责定义视频中角色的视觉身份，通过标准化的角色设定集（Character Sheet）确保角色在全片中的视觉一致性。

## 2. 使用时机
- 在风格定稿后，需要为剧本中的角色建立视觉形象时。

## 3. 执行指令
1. **角色画像提取**：分析性格、职业、背景。
2. **视觉锚点定义**：确定不可变特征。
3. **设定图生成与迭代**：
   - **初次生成**：调用 `python 04-character-design/scripts/gen_image.py --prompt "[Prompt]" --output "04-character-design/characters/[name]/turnaround.png"`。
   - **迭代修改**：若用户提供原图及修改要求，调用 `python 04-character-design/scripts/gen_image.py --prompt "[修改要求]" --base_image "[原图路径]" --output "[新版本路径]"`。
   - **三视图 (Turnaround)**：正面、侧面、背面。
   - **表情特写 (Expression Sheet)**：至少包含 4 种核心情绪。

## 4. 交付物与存放位置
- **角色设定目录**: `04-character-design/characters/[character_name]/`
- **三视图**: `turnaround.png`
- **表情特写**: `expressions.png`
- **角色配置文件 (JSON)**: `config.json`
- **工具脚本**: `04-character-design/scripts/`
- **参考资料**: `04-character-design/references/`

## 5. 约束与规范
- 必须使用纯色背景以突出角色。
- 角色特征必须在所有图中保持高度统一。
- 交付物必须严格存放在 `04-character-design/characters/` 对应子目录下。

## 6. 示例
```json
{
  "character_name": "艾米利亚",
  "visual_anchors": ["银色机械左臂", "红色短发"],
  "color_palette": { "hair": "#FF0000", "suit": "#0000FF" },
  "prompt_trigger": "Emilia, red short hair, silver robotic left arm, turnaround sheet"
}
```

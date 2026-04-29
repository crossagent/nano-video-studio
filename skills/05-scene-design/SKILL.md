---
name: "video-scene-design"
description: "负责视频场景的空间布局与环境设定。当需要设计背景、确定光影基准或管理场景资产时调用。触发词：'设计场景'、'场景设定'、'环境设计'。"
---

# 场景设定 (Video Scene Design)

## 1. 技能描述
本技能负责构建视频故事发生的物理空间，通过场景设定集确保空间逻辑严密、视觉连贯且符合叙事需求。

## 2. 使用时机
- 在剧本场景划分完成后。

## 3. 执行指令
1. **场景需求分析**：识别场景的功能性与情感基调。
2. **空间布局规划 (Layout)**：明确主体活动区域与背景区域。
3. **设定图生成**：
   - 调用 `skills/05-scene-design/scripts/` 下的生成脚本（如 `gen_scene.py`）。
   - 参考 `skills/05-scene-design/references/` 中的场景库或光影规范。
   - 产出高保真场景概念图（Concept Art）。

## 4. 交付物与存放位置
- **场景设定目录**: `skills/05-scene-design/scenes/[scene_name]/`
- **场景概念图**: `concept.png`
- **平面布局图**: `layout_map.png`
- **场景配置文件 (JSON)**: `config.json`
- **工具脚本**: `skills/05-scene-design/scripts/`
- **参考资料**: `skills/05-scene-design/references/`

## 5. 约束与规范
- 必须明确物体的相对方位，严禁空间逻辑冲突。
- 场景风格必须与 `03-art-style` 保持一致。
- 交付物必须严格存放在 `skills/05-scene-design/scenes/` 对应子目录下。

## 6. 示例
```json
{
  "scene_name": "遗忘实验室",
  "layout": "圆形空间，直径10米，培养皿位于圆心",
  "lighting": "冷色调，顶部点光源，培养皿自发光",
  "key_assets": ["发光培养皿", "生锈的操作台"]
}
```

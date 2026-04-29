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
   - 调用 `python skills/00-common-tools/scripts/gen_image.py --prompt "[Prompt]" --output "assets/05-scene-design/scenes/[name]/concept.png"`。
   - 参考 `assets/05-scene-design/references/` 中的场景库或光影规范。
   - 产出高保真场景概念图（Concept Art）。

## 4. 场景设计深度与广度 (Depth & Scope)
场景设计应涵盖以下维度：
- **室内场景 (Indoor)**：内部装饰、家具布局、功能区划分。
- **室外场景 (Outdoor)**：自然环境、地形地貌、外部氛围。
- **建筑结构设计图 (Architecture)**：建筑外观、结构透视、空间比例。

## 5. 交付物与存放位置
- **场景设定说明书 (Markdown)**: `assets/05-scene-design/scenes/[name]/scene_guide.md`
- **场景概念总图 (Total Map/Concept)**: `concept.png` (场景的全局氛围与核心视角)
- **室内/室外细节图 (Detail Maps)**: `details/[indoor_or_outdoor].png`
- **建筑结构图 (Structure)**: `details/architecture.png`
- **平面布局图 (Layout)**: `layout_map.png`
- **参考资料**: `assets/05-scene-design/references/`

## 6. 场景设定说明书 (scene_guide.md) 结构规范
文档应遵循“总-分”结构，包含以下内容：
1. **设计点描述**：描述场景的功能、情感基调、光影规范、地理位置及核心资产。
2. **图片简介表格**：
   | 图片名称 | 存放路径 | 内容简介 | 备注 |
   | :--- | :--- | :--- | :--- |
   | 场景概念总图 | concept.png | 场景的全局氛围、光影与视觉基调 | 总图 |
   | 室内细节 | details/indoor.png | 内部装饰细节与空间利用 | 分图 |
   | 室外环境 | details/outdoor.png | 外部环境、植被或地形 | 分图 |
   | 建筑结构图 | details/architecture.png | 建筑的结构透视、外观设计与比例 | 分图 |
   | 平面布局图 | layout_map.png | 空间的俯视布局与物体相对位置 | 分图 |

## 7. 约束与规范
- 必须明确物体的相对方位，严禁空间逻辑冲突。
- 场景风格必须与 `03-art-style` 保持一致。
- **禁止使用 JSON 配置文件**，所有场景设定必须记录在 `scene_guide.md` 中。
- 交付物必须严格存放在 `assets/05-scene-design/scenes/` 对应子目录下。

## 8. 示例 (scene_guide.md 片段)
### 设计点描述
场景“遗忘实验室”是一个位于荒漠中的圆形科研设施。
基调：压抑、科幻、冷色调。
核心资产：中央发光培养皿、生锈的操作台。

### 图片简介
| 图片名称 | 存放路径 | 内容简介 | 备注 |
| :--- | :--- | :--- | :--- |
| 实验室总图 | concept.png | 全景展示实验室内部氛围与中心培养皿 | 总图 |
| 建筑外观 | details/architecture.png | 实验室在荒漠中的球形建筑外观 | 分图 |

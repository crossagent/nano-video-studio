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
1. **资产检索**：
   - **必须**先读取 `[project]/assets/03-art-style/style_guide.md` 以获取全片的视觉基调。
   - **必须**使用 `[project]/assets/03-art-style/style_reference.png` 作为底层风格参考。
2. **角色画像提取**：分析性格、职业、背景。
3. **视觉锚点定义**：确定不可变特征。
4. **生成任务流 (Generation Workflow)**：
   - **创建提案 (Propose)**：
     调用 `video-studio` MCP 服务的 `submit_image_task` 工具，明确 `channel_id`、`model_id`、`project`、`stage` ('character-design') 及 `extra_params`。
   - **获取审批**：向用户汇报任务 ID 及参数，等待批准。
   - **触发执行 (Execute)**：
     审批通过后，调用 `video-studio` MCP 服务的 `approve_task` 和 `execute_task` 工具完成渲染。

## 4. 角色设定图核心要素 (Core Elements)
为了确保角色一致性，一张完整的设定图应包含以下要素：
- **全身三视图**：正面、侧面、背面，展示完整的体型与服装。
- **核心表情组**：至少包含 4-5 种代表性情绪（如：喜、怒、哀、惊、诱惑）。
- **视觉锚点 (Visual Anchors)**：角色不可变的特征（如：腰间魅魔纹、高马尾）。
- **服装细节**：明确的衣着款式（如：吊带、1分裤）。
- **色板 (Color Palette)**：标注头发、皮肤、服装的主色调。

## 5. 交付物与存放位置
- **角色设定说明书 (Markdown)**: `[project]/assets/04-character-design/characters/[name]/character_guide.md`
- **角色综合设定图 (Total Map)**: `character_sheet.png` (包含全身、核心表情、核心细节)
- **三视图 (Turnaround)**: `turnaround.png`
- **表情特写 (Expression Sheet)**: `expressions.png`
- **视觉锚点/细节图 (Detail Maps)**: `details/[feature].png`
- **参考资料**: `[project]/assets/04-character-design/references/`

## 6. 角色设定说明书 (character_guide.md) 结构规范
文档应遵循“总-分”结构，包含以下内容：
1. **设计点描述**：描述角色的性格、视觉特征、视觉锚点（不可变特征）及核心色板。
2. **图片简介表格**：
   | 图片名称 | 存放路径 | 内容简介 | 备注 |
   | :--- | :--- | :--- | :--- |
   | 角色综合设定图 | character_sheet.png | 包含全身、表情组、视觉锚点等的综合大图 | 总图 |
   | 三视图 | turnaround.png | 角色的正面、侧面、背面标准化展示 | 分图 |
   | 表情特写 | expressions.png | 包含至少4种核心情绪的表情集合 | 分图 |
   | [细节图名称] | details/[name].png | 展示特定的视觉锚点（如机械臂、纹身等） | 分图 |

## 7. 约束与规范
- 必须使用纯色背景以突出角色。
- 角色特征必须在所有图中保持高度统一。
- **禁止使用 JSON 配置文件**，所有角色设定必须记录在 `character_guide.md` 中。
- 交付物必须严格存放在 `[project]/assets/04-character-design/characters/` 对应子目录下。

## 8. 示例 (character_guide.md 片段)
### 设计点描述
角色“艾米利亚”是一名冷静的机械师。
核心特征：银色机械左臂，红色短发。
色板：头发 #FF0000，皮肤 #FFDAB9，机械臂 #C0C0C0。

### 图片简介
| 图片名称 | 存放路径 | 内容简介 | 备注 |
| :--- | :--- | :--- | :--- |
| 艾米利亚总图 | character_sheet.png | 综合展示艾米利亚的外形与表情基调 | 总图 |
| 银色机械臂细节 | details/robotic_arm.png | 详细展示机械臂的构造与反光质感 | 分图 |

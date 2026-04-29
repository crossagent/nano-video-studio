---
name: "video-art-style"
description: "定义视频的全局艺术风格与视觉基调。当需要设定色彩规范、艺术流派或生成全局 Prompt 风格后缀时调用。触发词：'设定风格'、'视觉基调'、'艺术风格'。"
---

# 艺术风格设定 (Video Art Style)

## 1. 技能描述
本技能负责为视频建立统一的视觉语言。通过定义艺术流派、色板和 Prompt 规范，并产出高保真的风格参考图，确保全片所有镜头在视觉质感上保持高度一致。

## 2. 使用时机
- 在剧本定稿后，开始视觉生成前。

## 3. 执行指令
1. **风格调研**：推荐匹配的艺术流派。
2. **色板定义**：选定主色、辅助色和强调色。
3. **Prompt 模板构建**：生成用于 AI 绘图的正面后缀和负面提示词。
4. **风格参考图生成**：
   - 调用 `python skills/00-common-tools/scripts/gen_image.py --prompt "[Prompt]" --output "assets/03-art-style/style_reference.png"`。
   - 参考 `assets/03-art-style/references/` 中的风格库。
   - 产出 1-3 张代表全片视觉最高标准的“风格样帧”。

## 4. 交付物与存放位置
- **艺术风格说明书 (Markdown)**: `assets/03-art-style/style_guide.md`
- **风格参考图 (Total Map)**: `assets/03-art-style/style_reference.png`
- **细节参考图 (Detail Maps)**: `assets/03-art-style/details/[feature].png`
- **参考资料**: `assets/03-art-style/references/`

## 5. 艺术风格说明书 (style_guide.md) 结构规范
文档应遵循“总-分”结构，包含以下内容：
1. **设计点描述**：详细描述视觉风格、色彩规范、光影基准及 Prompt 核心词。
2. **图片简介表格**：
   | 图片名称 | 存放路径 | 内容简介 | 备注 |
   | :--- | :--- | :--- | :--- |
   | 全局风格参考图 | style_reference.png | 展示全片的视觉基调、核心色彩与光影 | 总图 |
   | [细节图名称] | details/[name].png | 描述该细节图展示的具体材质、光效或元素 | 分图 |

## 6. 约束与规范
- 交付物必须严格存放在 `assets/03-art-style/` 目录下。
- **工作流约束**：风格参考图仅用于引导角色和场景的生成，**禁止**将其直接作为参考图传递给分镜（Storyboard）生成工具，以避免干扰模型对镜头内容的理解。

## 7. 示例 (style_guide.md 片段)
### 设计点描述
本片采用“赛博朋克写实风格”，主色调为霓虹深蓝与暗金。光影强调高对比度，冷暖光交替。
Prompt 核心：`cyberpunk realism, high contrast, neon lighting, 8k, cinematic`

### 图片简介
| 图片名称 | 存放路径 | 内容简介 | 备注 |
| :--- | :--- | :--- | :--- |
| 赛博朋克总图 | style_reference.png | 定义全片的高对比度冷暖视觉基调 | 总图 |
| 霓虹灯光细节 | details/neon_detail.png | 展示霓虹灯在雨水地面的反射质感 | 分图 |

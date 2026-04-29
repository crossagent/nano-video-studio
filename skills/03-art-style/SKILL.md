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
   - 调用 `skills/03-art-style/scripts/` 下的生成脚本（如 `generate_style.py`）。
   - 参考 `skills/03-art-style/references/` 中的 API 文档或风格库。
   - 产出 1-3 张代表全片视觉最高标准的“风格样帧”。

## 4. 交付物与存放位置
- **风格参考图**: `skills/03-art-style/style_reference.png`
- **风格配置文件 (JSON)**: `skills/03-art-style/style_config.json`
- **风格参考说明 (Markdown)**: `skills/03-art-style/style_guide.md`
- **工具脚本**: `skills/03-art-style/scripts/`
- **参考资料**: `skills/03-art-style/references/`

## 5. 约束与规范
- 所有关键词和参考图必须服务于同一种艺术流派。
- 交付物必须严格存放在 `skills/03-art-style/` 目录下。

## 6. 示例
```json
{
  "style_name": "未来主义写实",
  "positive_suffix": "cinematic lighting, 8k resolution, photorealistic",
  "negative_prompt": "cartoon, anime, sketch",
  "color_palette": { "primary": "#001219", "accent": "#ee9b00" },
  "reference_images": ["style_reference.png"]
}
```

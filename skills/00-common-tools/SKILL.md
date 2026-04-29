---
name: "common-tools"
description: "提供视频生产流水线通用的自动化脚本与工具。当需要调用图像生成、文件处理或其他跨阶段通用功能时调用。"
---

# 通用工具集 (Common Tools)

## 1. 技能描述
本技能作为整个流水线的“工具箱”，存放所有可复用的自动化脚本。通过统一管理，降低维护成本，确保各阶段调用的工具逻辑一致。

## 2. 使用时机
- 当其他 Skill 需要执行具体的自动化任务（如生图、视频合成）时。
- 需要维护或更新全局通用的 API 调用逻辑时。

## 3. 核心工具说明
### 图像生成工具 (`gen_image.py`)
- **路径**: `skills/00-common-tools/scripts/gen_image.py`
- **功能**: 统一生图入口。支持 OpenRouter (GPT-5.4) 和 火山引擎 (Seedream)。
- **逻辑**: 如果 `--model` 包含 `doubao-`，则调用火山引擎 API；否则调用 OpenRouter。
- **参数**:
  - `--prompt`: 生成指令。
  - `--output`: 输出路径。
  - `--stage`: (可选) 任务阶段，可选 `style`, `character`, `scene`, `storyboard`。会自动读取对应的环境变量。
  - `--model`: (可选) 直接指定模型名称，会覆盖 stage 配置。
  - `--size`: (可选) 图片尺寸，支持 `1K`, `2K` 等。
  - `--aspect_ratio`: (可选) 图片比例（仅 OpenRouter 支持）。
25: 
26: ### 视频生成工具 (`gen_video.py`)
27: - **路径**: `skills/00-common-tools/scripts/gen_video.py`
28: - **功能**: 调用火山引擎 (Volcengine Ark) Doubao/Seedance API 生成视频。
29: - **参数**:
30:   - `--prompt`: 视频动作及场景描述。
31:   - `--output`: 输出视频路径 (.mp4)。
32:   - `--images`: (可选) 参考分镜图路径或 URL。
33:   - `--videos`: (可选) 参考视频 URL。
34:   - `--audios`: (可选) 参考音频 URL。
35: - **注意**: 视频生成为异步任务，脚本会自动轮询状态并下载结果。时长与比例由 `.env` 配置决定。

## 4. 约束与规范
- 所有新开发的通用脚本必须存放在 `scripts/` 目录下。
- 脚本必须支持从根目录的 `.env` 文件读取配置。
- 跨阶段调用的路径必须使用相对于项目根目录的完整路径。

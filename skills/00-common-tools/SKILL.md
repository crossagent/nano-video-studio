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

### 任务管理与自动化 (Task Management)
- **数据库路径**: `generation_tasks.db`
- **管理脚本**: `skills/00-common-tools/scripts/task_db.py`
- **执行引擎**: `skills/00-common-tools/scripts/run_task.py`
- **核心逻辑**: 所有昂贵的生成任务必须遵循：**提交提案 (Propose) -> 用户审批 (Approve) -> 触发执行 (Execute)**。

## 3. 核心工具说明
### 图像生成工具 (`gen_image.py`)
- **路径**: `skills/00-common-tools/scripts/gen_image.py`
- **功能**: 统一生图底层驱动。由 `run_task.py` 内部调用。
- **注意**: 严禁直接从生产 Skill 调用此脚本，必须通过 `run_task.py` 间接调用。
- **参数**:
  - `--prompt`: 生成指令。
  - `--output`: 输出路径。
  - `--stage`: (可选) 任务阶段，可选 `style`, `character`, `scene`, `storyboard`。会自动读取对应的环境变量。
  - `--model`: (可选) 直接指定模型名称，会覆盖 stage 配置。
  - `--size`: (可选) 图片尺寸，支持 `1K`, `2K` 等。
  - `--aspect_ratio`: (可选) 图片比例（仅 OpenRouter 支持）。

### 视频生成工具 (`gen_video.py`)
- **路径**: `skills/00-common-tools/scripts/gen_video.py`
- **功能**: 统一视频底层驱动。由 `run_task.py` 内部调用。
- **注意**: 严禁直接从生产 Skill 调用此脚本，必须通过 `run_task.py` 间接调用。
- **参数**:
  - `--prompt`: 视频动作及场景描述。
  - `--output`: 输出视频路径 (.mp4)。
  - `--images`: (可选) 参考分镜图路径或 URL。
  - `--videos`: (可选) 参考视频 URL。
  - `--audios`: (可选) 参考音频 URL。
- **注意**: 视频生成为异步任务，脚本会自动轮询状态并下载结果。时长与比例由 `.env` 配置决定。

## 4. 约束与规范
- 所有新开发的通用脚本必须存放在 `scripts/` 目录下。
- 脚本必须支持从根目录的 `.env` 文件读取配置。
- 跨阶段调用的路径必须使用相对于项目根目录的完整路径。

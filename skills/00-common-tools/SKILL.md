---
name: "common-tools"
description: "提供视频生产流水线通用的自动化脚本与工具。当需要调用图像生成、文件处理或其他跨阶段通用功能时调用。"
---

# 通用工具集 (Common Tools)

## 1. 技能描述
本技能作为整个流水线的“工具箱”，存放所有可复用的自动化脚本。

## 2. 使用时机
- 执行具体的自动化任务（如生图、视频合成）时。
- 必须通过 MCP 接口进行操作，严禁直接运行脚本。

### 任务管理与自动化 (MCP Server)
- **服务路径**: `skills/00-common-tools/scripts/nano_video_mcp.py`
- **传输协议**: MCP (Model Context Protocol)

## 3. 核心工具说明 (MCP Tools)

AI 应当优先调用 `nano_video_mcp.py` 暴露的以下工具：

1. **`list_available_models`**: 查询支持的渠道、模型及其必填参数要求。**在提交任务前应先通过此工具确认参数规范。**

2. **`submit_image_task`**: 提交一个新的图像生成提案。
   - `channel_id`: 必填（如 `openrouter`, `volcengine`）。
   - `model_id`: 必填（如 `doubao-seedream-5-0-260128`）。
   - `extra_params`: 必填。字典格式，必须包含该模型要求的参数（如 `size`）。

3. **`submit_video_task`**: 提交一个新的视频生成提案。
   - `channel_id`: 必填。
   - `model_id`: 必填。
   - `extra_params`: 必填。必须包含视频模型要求的参数（如 `duration`, `aspect_ratio`）。

4. **`approve_task`**: 审批通过一个任务。
5. **`execute_task`**: 正式触发任务执行。
6. **`list_tasks`**: 查看特定模型表的任务列表。
7. **`get_task_details`**: 获取任务详情。

## 4. 校验规则与约束
- **参数预审**: 服务器会在写入数据库前强制校验 `channel_id`、`model_id` 以及对应的 `required_fields`。
- **类型匹配**: 视频模型严禁通过 `submit_image_task` 提交，反之亦然。
- **错误处理**: 如果参数不完整，接口将返回 `Validation Error` 及其缺失的字段列表。
- **禁止绕过**: 严禁 AI 直接通过 shell 调用底层脚本。
- **状态追踪**: 必须严格遵循 `submit -> approve -> execute` 的生命周期。

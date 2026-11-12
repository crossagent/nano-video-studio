# Platform 平台能力

`platform/` 统一管理影视工程对接的底层生成与制作引擎，提供标准化的自动化执行接口与调用适配器。

---

## 包含平台引擎

1. **`blender/` (Blender 3D 制作引擎)**：
   - 影视 3D 分镜预演（Previs）、相机调度轨迹（Camera Blocking）、粗模搭建与视口渲染快照；
   - 统一由 `platform/blender/run.ps1` 调度，任务文件存放在 `tasks/blender/<task-id>/`；
   - 详细接口与通用工具参见 [Blender 平台规范](blender/README.md)。

2. **`comfyui/` (ComfyUI 本地图像与视频工作流)**：
   - 本地 ComfyUI HTTP API 批量执行接口；
   - 详细接口参见 [ComfyUI 接入说明](comfyui/README.md)。

3. **`seedance/` (火山引擎 Doubao Seedance API)**：
   - 火山方舟视频生成异步任务与 Files API 客户端（纯 Python 标准库实现，零第三方依赖）；
   - 支持离线配置校验、`--dry-run` 预演、自动上传白模视频并提交参考生视频任务；
   - 详细接口参见 [Seedance 接入说明](seedance/README.md)。

## CapCut 桌面版

本机通过 `capcut_local` stdio MCP 操作 CapCut 草稿。接入代码在 `platform/capcut-local/` 单独检出，当前使用 `JmsLdrn/capcut-mcp` 的 `50beafd` 提交。本机草稿目录和操作约定见[项目 README](../README.md#capcut-桌面剪辑)，单次剪辑的路径和验收记录见[任务索引](../tasks/README.md#capcut-capcut)。

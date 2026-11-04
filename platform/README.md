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

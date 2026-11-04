# Platform

提供通用生图、生视频能力。当前后端为本地 ComfyUI，入口见 [comfyui](comfyui/README.md)。

- 本工程拥有资产、任务要求、工作流版本、调用记录与收回的结果。
- ComfyUI 拥有独立安装、Python 环境、模型、自定义节点与运行队列，不作为本仓库子目录或子模块。
- 仅通过 HTTP API 集成；不修改 ComfyUI 源码、不共用虚拟环境、不接管其更新。
- 升级可能改变节点接口。工作流应记录所用 ComfyUI 版本、自定义节点版本与模型文件，升级后用图形界面回归验证。
- 生成入口统一为 ComfyUI HTTP API；旧云端生成 MCP 工具已移除。

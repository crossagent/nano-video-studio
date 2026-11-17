# 第一幕 UI 视频验证

状态：review（十镜生成完成，待连续运动及画面复核）。目标：在现有 ComfyUI 中以白模视频与分镜图为参考，先验证单镜头，再逐镜生成并评估。候选保留在本任务，不自动入库。

输入：`tasks/imagegen/act01-visual-storyboards/output/shots/`；现有工作流 `platform/comfyui/workflows/starcraft-act01-previs-to-video.ui.json`。白模 24 fps；01–08 各 3 秒，09 为 4 秒，10 为 5 秒，作为目标时长。视觉图为约 3.4:1，白模约 2.39:1；08 视觉图基于第 545 帧而非首帧 505。验收需逐镜检查构图、主体相对位置、镜头运动与生成时长；不能仅凭提示词判定成功。

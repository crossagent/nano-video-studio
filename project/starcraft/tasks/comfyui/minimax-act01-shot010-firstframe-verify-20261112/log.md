# 执行记录

- 2026-11-12 由 `image-generator` 依据 S01-010 白模第 0 帧与 `style-canyon-wheat.jpg` 独立生成写实首帧，裁除黑边并匹配 608:256 比例保存为 `inputs/s01-010-firstframe-gen.png`（不依赖任何 Seedance 成片帧）。
- 2026-11-12 16:47 提交 `Ref2VA + MiniMaxH3AddGuide(frame_idx=0)` 20 步验证任务（`prompt_id`: `3db37e0d-40a1-4b25-adf1-9e21d30a0f44`），关联单次运行档案 `tasks/comfyui/minimax-shot010-firstframe-verify-20261112/`。
- 2026-11-12 17:47 ComfyUI 执行完成（耗时 `00:59:10`，20 步、608×256、158 帧、24 fps）。已收集原片并裁除尾部 14 帧补帧，保存为 `output/s01-010-firstframe-verify-144f.mp4`（144 帧、6.00 秒），并生成四路同步对照 `output/comparison-s01-010-firstframe-verify.mp4`。
- 审阅结论：
  1. **彻底消除灰模残留与末段跳图**：从 0.0s 到 5.8s 全程为电影级写实画面（黑岩山口、左弯溪流、右直泥路、翻滚金黄麦田、暴雨与双道紫白闪电），无任何 Blender 灰模滞留，也未发生末段跳回无关风景图的问题。
  2. **确认 `Ref2VA + AddGuide(frame_idx=0)` 协同可用**：`MiniMaxH3AddGuide` 在 `minimax_h3_ref2va` 权重上成功锁死第 0 帧写实起点，并跟随 `<Video 1>` 完成了越脊俯冲到贴地平视的完整运镜。
  3. **首帧透视与节奏耦合**：因 `AddGuide` 强锁定第 0 帧，若首帧画面相对白模第 0 帧多画出了顶部天空与更远视野，前中段越脊速度会比白模略慢约 0.8–1.0 秒；若要严格贴合白模帧对帧时序，首帧图必须严格按白模第 0 帧裁景（不额外补出白模视野外的天空）。

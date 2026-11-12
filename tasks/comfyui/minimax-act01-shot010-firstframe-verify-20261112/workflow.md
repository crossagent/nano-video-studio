# 工作流

使用 `minimax_h3_ref2va_pruned_int8_convrot.safetensors`，20 步基础采样（`res_multistep` + `beta`，无加速 LoRA），输出 `608×256`、158 帧、24 fps。

关键节点改动：
1. `MiniMaxH3ReferenceToVideo`：仅传入 `<Video 1>`（白模 `s01-010-guide.mp4`）与 `<Picture 1>`（独立写实首帧 `s01-010-firstframe-gen.png`），移除无关的收割机 `<Picture 2>`。
2. `MiniMaxH3AddGuide`（`frame_idx = 0`）：将 `s01-010-firstframe-gen.png` 硬锚定到生成视频第 0 帧（`minimax_keyframes`），与 `minimax_refs` 一并送入 DiT，检验“首帧锁死 + 白模运动引导”的效果。

# MiniMax H3 独立首帧 + 白模高空俯冲验证（S01-010）

- 状态：review
- 目标：验证在**不使用任何 Seedance 成片帧**的前提下，仅靠“独立生成的高空俯冲写实首帧 + 原始白模视频”，MiniMax H3（`ref2va` + `MiniMaxH3AddGuide` 首帧锚定 + 20 步）能否正确完成最难的高空越脊俯冲镜头，彻底消除灰模残留与末段吸附。
- 输入：
  - 白模视频：`tasks/comfyui/minimax-act01-optimize-20261110/inputs/s01-010-guide.mp4`（158 帧，前 144 帧为 S01-010 原白模 + 14 帧尾部补帧适配 `17n+5`）
  - 独立首帧：`tasks/comfyui/minimax-act01-shot010-firstframe-verify-20261112/inputs/s01-010-firstframe-gen.png`（由 `image-generator` 依据白模第 0 帧与 `style-canyon-wheat.jpg` 独立生成并裁至 2.375:1）
- 验收：检查 0s、2s、4s、5.5s–6s 是否全程保持高空越脊俯冲构图、山脊与麦田是否彻底转为写实材质、末段是否不再跳回无关风景图。

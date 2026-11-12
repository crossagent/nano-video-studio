# 执行记录

- 2026-11-11 用户要求采用 Seedance 那次相同的素材，不以 Seedance 成片作为参考。
- 核对 Seedance 成功任务 `execution.json`，场景图 SHA-256 为 `80413000d5df41b9985e815b9b48e75ad9c1f56a8401f334c71b72856c128087`，车辆局部图为 `c23f535e7762b285a8d72098d5a0b9b4443efff64043c071c7c2045577689e71`。白模源文件 SHA-256 为 `9a2202015d21ab3f8318f68e7c068b62e2b7301aa21af3a3bfc0eba156874e3a`。
- 2026-11-11 22:32 顺序提交四镜 20 步工作流至本地 ComfyUI（队列顺序 `020` → `010` → `030` → `040`）：
  - `minimax-original-shot020-20261111`（`e7dfd584-b1d1-42ef-8b07-330a723b8fa2`）：ComfyUI 日志耗时 `00:23:53`，于 `2026-11-11 22:56:29` 生成 `minimax-original-shot020-20261111_00001_.mp4`（90 帧、608×256、24 fps）。
  - `minimax-original-shot010-20261111`（`f7b9554e-c147-4ae0-9e5b-ca22f294fdab`）：ComfyUI 日志耗时 `00:53:26`，于 `2026-11-11 23:49:56` 生成 `minimax-original-shot010-20261111_00001_.mp4`（158 帧、608×256、24 fps）。
  - `minimax-original-shot030-20261111`（`74e8c311-83e1-4fd0-8033-61a2a610eca0`）：ComfyUI 日志耗时 `00:12:06`，于 `2026-11-12 00:02:04` 生成 `minimax-original-shot030-20261111_00001_.mp4`（73 帧、608×256、24 fps）。
  - `minimax-original-shot040-20261111`（`bef89e4b-69fb-41ac-ae13-bf0b60931ce9`）：ComfyUI 日志耗时 `00:43:44`，于 `2026-11-12 00:45:48` 生成 `minimax-original-shot040-20261111_00001_.mp4`（141 帧、608×256、24 fps）。
- 2026-11-12 已将 ComfyUI 共享输出目录的四段视频收集归档至各自任务目录 `output/` 并补充 `outputs.json`；裁除尾部补帧（分别保留 `144`、`84`、`72`、`132` 帧）后无声拼接为 `output/minimax-four-shot-original-inputs.mp4`（432 帧、18.00 秒、608×256、24 fps），同时生成四路同步对照 `output/four-way-comparison-original.mp4`（左上白模、右上 Seedance 2.5、左下 MiniMax 含 Seedance 帧优化版、右下本轮 MiniMax 原始参考图版）。
- 抽帧审阅与对照结论：
  1. **S01-020 与 S01-030（静机位近景）彻底摆脱白模残留**：即使完全不用 Seedance 帧，只要拆成单镜 + 20 步基础采样（去掉 4 步加速 LoRA）+ 结构化 `Ref2VA` 提示词，`020` 能生成湿润黑色玄武岩与同步雷击碎裂，`030` 甚至因接入 `<Picture 2>` 而渲染出比“Seedance 同机位帧版”更清晰的红色车体与金属履带轮系。
  2. **S01-010（大视角俯冲）仍残留白模且末段跳回参考图**：前 2 秒高空越脊俯冲中仅有局部块面转写实、山脊与条带仍保留明显 Blender 灰模，5.5 秒镜头压平后直接吸附回 `<Picture 1>`（平视风景图）构图；另本次工作流错误在该镜仍挂载了 `<Picture 2>`（收割机图）。
  3. **S01-040（英雄载具中景）质感写实但车头朝向随 `<Picture 2>` 反转朝左**：`minimax_h3_ref2va` 将 `<Picture 2>` 视为带固定结构与朝向的主体参考，无法像 Seedance 2.5 那样把朝左参考车体按白模朝右几何重投影。

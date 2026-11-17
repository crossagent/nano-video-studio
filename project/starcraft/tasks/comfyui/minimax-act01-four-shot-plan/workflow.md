# 本地 MiniMax H3 参考视频工作流

使用项目已有 `starcraft-act01-previs-to-video.api.json` 作为起点，由 `prepare.py` 生成任务专用图和双任务清单。两段均输入原 18 秒白模，通过 `VideoTemporalCrop` 取对应帧。两张图为之前 Seedance 实测使用的峡谷麦田裁图与 580×400 车辆材质裁图。

第一段输入 144 帧，输出 141 帧。第二段输入 288 帧，输出 294 帧。模型帧数按 5+17n 约束取值，因此拼接时需要对齐原切点并记录修整方式。两段独立生成，切点和场景的跨段一致性需要检查。

模型为本地 Ref2VA INT8，608×256、24 fps、20 步。提交与运行记录保存在 `tasks/comfyui/minimax-act01-wind-20261110/` 和 `tasks/comfyui/minimax-act01-strike-track-20261110/`。任务客户端负责记录工作流、提交 ID 并收集输出。

第二段采用下载并校验的 Ref2VA Turbo LoRA，采样改为 4 步，任务为 `tasks/comfyui/minimax-act01-strike-track-turbo-20261110/`。第一次 20 步第二段由执行者主动中断。生成帧数不足的首段在拼接时冻结末帧 3 帧，第二段裁去末尾 6 帧。为了只比较画面，拼接版没有音轨。

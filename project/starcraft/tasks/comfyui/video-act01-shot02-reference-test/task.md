# 第一幕镜头 02（收割机侧后跟拍）AI 视频生成与控制方案对照任务

- **任务状态**：completed
- **完成时间**：2026-11-05 18:20
- **日期**：2026-11-05 (Asia/Shanghai)
- **对应分镜**：第一幕 Shot 02（联合收割机 · 侧后 45° 高速追随跟拍，长方体低模车身在风暴麦田中前进）
- **核心研究目标**：
  解决 Blender 粗模（Low-Poly Blockout）在视频生成中的边缘对齐与语义替换矛盾，验证：
  1. 为什么 ControlNet 1.0 强控会导致潜空间锁死并原样输出 Blender 方块；
  2. 方案 A（纯隐空间参考）与 方案 B（ControlNet 降权与时间步退火）的生成质量差异。
- **输入资产**：
  - 分镜视频：`tasks/blender/previs-blocking-act-001/output/starcraft_previs_act01_unique_20261104.mp4`（帧 72~144，去字裁剪为 768×256）
  - 场景参考图：`assets/settings/scenes/scene-01-bhekar-ro-wheatfield-storm.jpg`（拜卡罗风暴麦田与帝国工业收割机）
- **生产软件与硬件**：
  - ComfyUI Desktop (RTX 5060 Ti 16GB)
  - 底模：MiniMax H3 Ref2VA (`minimax_h3_ref2va_pruned_int8_convrot.safetensors`)
  - 文本/多模态视觉编码器：`qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
  - 视频 VAE：`minimax_h3_video_vae_int8_convrot.safetensors`
  - 控制网插件：`minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors`
- **生成规格**：
  - 画幅：768 × 256（约 3:1 超宽画幅，去除白模字幕遮罩）
  - 帧率：24.0 fps，73 帧（3.04 秒）
  - 采样步数：20 步 (Beta Scheduler / res_multistep)
  - 固定种子：`2026110412`（保证绝对客观对照）

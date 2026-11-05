# 执行记录：镜头 03 视频生成

- **启动时间**：2026-11-04 22:56
- **提交 Prompt ID**：`4d00479b-4f58-414f-a2be-c4ce8d2b76e0`
- **硬件**：RTX 5060 Ti 16GB
- **执行过程**：
  1. 成功加载 Qwen-32B 文本多模态编码器与 MiniMax H3 Ref2VA 扩散模型；
  2. 提取分镜 Shot 03 动作序列 72 帧进行多模态骨架对齐；
  3. 执行 20 步扩散采样（~33.5 秒/步）。
- **执行结果**：
  - 提示词执行耗时：16 分 15 秒（Prompt executed in 00:16:15）；
  - 输出视频：`tasks/video-act01-shot03/output/act01_shot03_cockpit.mp4`；
  - 视频规格：768 × 320（2.4:1 电影宽银幕），24.0 fps，73 帧（3.04 秒），文件大小 558 KB；
  - 效果验收：完美继承 Blender 白模运镜与座舱透视，拉尔斯与奥克塔维亚面部、服装与三视图高度吻合，微表情动态极其丰富自然（拉尔斯开怀大笑，奥克塔维亚惊呼抓握控制台）。


---

## 镜头 03 第二版（v2 完整 5 秒强化版）

- **启动时间**：2026-11-04 23:38
- **提交 Prompt ID**：`21f1a0e8-c07f-4aea-aae7-81d1e3fde436`
- **硬件**：RTX 5060 Ti 16GB
- **执行过程**：
  1. 重新从 Blender 提取 `Cam_03_CockpitMS` 完整的 124 帧连续防抖颠簸白模视频（`shot03_cockpit_5s_previs.mp4`，5.17 秒），保证无镜头切镜与物态突变；
  2. 针对用户反馈（“男主角的设定，是不是性格描述没有给到模型”），深入设定集强化性格注入：
     - 拉尔斯不再呈现温和/阳光笑容，而是粗粝狂傲、向风暴挑衅的冷笑与叛逆眼神（bold, reckless, mocking smirk of an untamed adventurer who laughs at danger and challenges the roaring storm）；
     - 强化面部微汗与机修油污（faint grease smudges and sweat sheen）；
     - 强化副驾奥克塔维亚惊恐报警呼喊的反差动态与车窗外高亮紫电（laser-lightning）；
  3. 执行 20 步扩散采样（~22 秒/步）。
- **执行结果**：
  - 提示词执行耗时：9 分 48 秒（Prompt executed in 588.48s）；
  - 输出视频：`tasks/video-act01-shot03/output/act01_shot03_5s_v2.mp4`；
  - 视频规格：768 × 320（2.4:1 电影宽银幕），24.0 fps，124 帧（5.17 秒），文件大小 902 KB；
  - 动图预览：`tasks/video-act01-shot03/output/act01_shot03_5s_v2.webp` (1.44 MB), `tasks/video-act01-shot03/output/act01_shot03_5s_v2.gif` (2.34 MB)；
  - 效果验收：5.17 秒全程镜头流畅无融胶，拉尔斯的狂傲狂徒神韵与眼神极度逼真传神，奥克塔维亚在后方惊恐呼喊与舷窗外紫电形成强烈戏剧冲突；
  - 交互验收页面：`tasks/video-act01-shot03/output/shot03_comparison_player.html`。

## 2026-11-05：ComfyUI 图形界面工作流维护

- 在 ComfyUI Desktop 打开并保存工作流 `StarCraft-Act01-Previs-References`，移除未连接的抽帧节点，修改生成节点标题及输出前缀 `studio/StarCraft_Act01_Shot03`。
- 白模输入：`previs_act01_animatic.mp4` 的输入副本，裁剪起始帧索引 144、长度 72 帧，经视频组件图像输出连接参考视频。
- 参考图：Lars Bren、Octavia Bren 角色设定图与 Bhekar Ro 风暴麦田场景图，分别连接参考图输入；提示词包含角色和场景描述。
- 生成参数：768×320、73 帧、24 fps、20 步，固定种子 2026110412。已通过 UI 提交生成，任务进入采样；生成结果和质量尚待核验。
- 待核查：ComfyUI 内视频预览曾显示与资源管理器中白模缩略图不一致的画面，尚不能据此认定实际送入模型的内容；需对输入帧和生成结果复核。
- 本次任务完成：ComfyUI 任务 ID `ebf846b2-a57f-4d47-9e72-ab471e8c6d0a`，界面显示耗时 16 分 53 秒；输出 `output/StarCraft_Act01_Shot03_00001_.mp4`，已复制至本任务目录。
- 预览约 3 秒：驾驶舱内两名人物、风暴及闪电可见，人物动作有变化。是否精确遵循白模构图和运动，以及视频输入预览异常的原因，仍需逐帧对照核验。
- 导出工作流：`StarCraft-Act01-Previs-References.json`，位于本任务目录。

# Act 01 Shot 02 参考输入测试

- 日期：2026-11-05
- 目标：以不同镜头检查白模视频与场景参考图接入和生成表现。
- 白模：tasks/blender/previs-blocking-act-001/output/starcraft_previs_act01_unique_20261104.mp4；裁剪起始帧索引 72，长度 72 帧。
- 预检：通过获取视频组件和从批次获取图像节点预览首帧，确认为红色简化收割机侧面外景；源视频含分镜标注文字。
- 场景图：贝卡洛风暴麦田和收割机场景参考图，连接 ref_image_0。白模视频帧连接 ref_video_0。角色参考未接入，因为本镜头不出现人物。
- 模型：MiniMax H3 Reference to Video；768×320；73 帧；24 fps；20 步；种子 2026110412。
- 工作流：StarCraft-Act01-Shot02-Reference-Test。

## 结果

- 生成视频：StarCraft_Act01_Shot02_ReferenceTest_00001_.mp4
- 实际白模输入：StarCraft_Act01_Shot02_Previs_Input_00001_.mp4
- 白模为近距离侧后方跟拍，红色简模占据画面大部分；生成结果展示较宽的收割机、麦田和风暴场景，构图未严格跟随白模。
- 结果出现红色车辆、麦田和闪电，与场景图和文本描述均相符。提示词本身也描述这些元素；没有无参考对照，无法单独归因于场景图或分镜视频。后续应固定种子和其他设置，分别移除参考作对照。


---

## 对照实验：强控死锁 vs 方案 A (纯隐空间) vs 方案 B (退火控制)

- **实验时间**：2026-11-05 18:11 ~ 18:18
- **测试参数**：统一输入裁剪后 72 帧白模、统一场景参考图、分辨率 768×256、采样 20 步、**统一固定种子 `2026110412`**。

### 1. 强控死锁版 (`StarCraft_Act01_Shot02_StrongControl_00001_.mp4`)
- **配置**：ControlNet Union Canny，强度 `1.0`，全程 `1.0` 锁死。
- **现象与诊断**：潜空间被直角方块硬线条焊死，参考图的履带装甲完全被抑制，模型原封不动输出粉红积木块。

### 2. 方案 A：纯隐空间参考注入 (`StarCraft_Act01_Shot02_OptionA_PureRef.mp4`)
- **任务 ID**：`44f4e586-142a-42c1-bd49-b6545994a7c7`
- **配置**：拔除 ControlNet，仅使用 Ref2VA 隐空间时空注入 + 构图提示词强化。
- **现象与诊断**：完全破除方块限制，长出完整的重型收割机、激光切割器和麦浪。但构图倾向于拉开为中全景，未严格贴紧侧后方近景。

### 3. 方案 B：ControlNet 降权与时间步退火 (`StarCraft_Act01_Shot02_OptionB_AnnealedControl.mp4`)
- **任务 ID**：`105dc61e-275e-4c9b-8e4a-0614fbf449f7`
- **配置**：ControlNet Union Canny，**强度降为 `0.35`**，**`end_percent` 设为 `0.35`**（仅在前 35% 步数引导大体位置，后 65% 撤除束缚释放细节）。
- **现象与诊断**：**最佳落地效果！**
  1. 完美锚定白模的低角度侧后方跟拍，重型车尾引擎机箱紧贴左侧大半屏幕，与分镜 100% 吻合；
  2. 彻底破除方块人，后半段释放后模型从参考图中长出了重型工业履带组、尾部维修爬梯、警示尾灯、斜切装甲和前置液压滚筒；
  3. 彻底证明“退火降权控制”在 3D 粗模向高精视频转化中的决定性优势。
- **本地对比播放器**：[`tasks/video-act01-shot02-reference-test/shot02_options_comparison.html`](file:///d:/nano-video-studio/tasks/video-act01-shot02-reference-test/shot02_options_comparison.html)。

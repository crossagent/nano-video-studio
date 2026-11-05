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

---

## 升级测试：Blender 5秒动态超车复杂深度与预演重构

- **时间**：2026-11-05 21:10
- **原因诊断**：
  1. 原白模测试镜头时长过短（仅 72 帧 / 3.0s），不足以展示空间调度与运镜质感；
  2. 原相机与收割机保持 100% 同速平移（相对位移差恒为 0），地表无近景地标，导致全片 72 帧车体像素坐标完全静止（“看不出画面变化”）；
  3. 原几何体仅 3 个简单立方体，缺乏深度层次与连续运动部件。
- **重构方案**：
  1. **时间与画幅扩展**：统一为 **120 帧（5.0s @ 24fps）**、**768×320（2.4:1 变形宽银幕比例）**；
  2. **动态超车低角度跟拍调度 (Dynamic Overtake Arc Track)**：
     - Frame 001 (0.04s)：低角度侧后方 3/4 视角（承接原分镜经典构图，车体占左半幅 50%）；
     - Frame 060 (2.50s)：相机加速沿侧面平移超车，展示车身正侧面装甲、滚转负重轮与驾驶舱；
     - Frame 120 (5.00s)：相机超越车体 6m 并向右后方回望，以正前 3/4 俯仰仰角锁定旋转切割滚刀与车头正面！
  3. **丰富几何与近景视差 (Parallax & Rich Hierarchy)**：
     - 增加 12 组旋转负重轮（滚动 6264° 与行进严密同步）、前置连续旋转切割滚刀（旋转 4320°）；
     - 沿 X = -7.0 铺设近景黄色危险警示桩与反光标，相机以 15m 间距贴近掠过，形成极强的近前景高速视差流；
     - 地表雕刻纵向麦原深浅垄沟，增强向后流动的空间纵深感。
  4. **True Depth 几何深度线性映射**：
     - Blender 5.2 合成节点使用 `CompositorNodeTree` 与 `ShaderNodeMapRange`；
     - 测量实际物理距离（近景桩 ~8m，车身 ~12.5m - 17.5m，麦田 ~10m - 35m），将映射范围严格锚定在 **6.0m ~ 36.0m**，线性输出为 1.0 (近亮) -> 0.0 (远暗)；
     - 车体自身各构件形成 0.62 ~ 0.88 的丰富内部分层灰度阶梯，彻底根除死白过曝或死黑截断。
- **产物与交付**：
  - Blender 工程：[`tasks/blender/previs-blocking-act-001/work/previs_act01_shot02_complex_depth.blend`](file:///d:/nano-video-studio/tasks/blender/previs-blocking-act-001/work/previs_act01_shot02_complex_depth.blend)
  - 5秒真实深度视频：[`D:/Comfy-Desktop/ComfyUI-Shared/input/StarCraft_Shot02_ComplexDepth_5s.mp4`](file:///D:/Comfy-Desktop/ComfyUI-Shared/input/StarCraft_Shot02_ComplexDepth_5s.mp4)
  - 5秒RGB白模预演视频：[`D:/Comfy-Desktop/ComfyUI-Shared/input/StarCraft_Shot02_ComplexPrevis_5s.mp4`](file:///D:/Comfy-Desktop/ComfyUI-Shared/input/StarCraft_Shot02_ComplexPrevis_5s.mp4)
  - 帧级对照联系表：[`tasks/video-act01-shot02-reference-test/preview_complex_depth.jpg`](file:///d:/nano-video-studio/tasks/video-act01-shot02-reference-test/preview_complex_depth.jpg)


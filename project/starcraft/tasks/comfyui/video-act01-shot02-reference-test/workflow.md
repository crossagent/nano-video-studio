# Shot 02 视频生成与控制方案对照工作流

## 1. 实验方案设计

为了验证“Blender粗模在视频生成中边缘无法对应、强控导致方块死锁”的问题，设计了三组对照实验：

### 对照组 1：强控死锁版 (StrongControl)
- **底层架构**：MiniMax H3 + ControlNet Union Canny
- **参数配置**：
  - Canny 算子：low_threshold: 0.05, high_threshold: 0.15
  - ControlNet 强度：`strength = 1.0`
  - 介入时间区间：`start_percent = 0.0, end_percent = 1.0`（全程锁死）
- **Prompt ID**：`45ccba0f-6f4d-42d0-ac00-a882c1116498`
- **输出产物**：`StarCraft_Act01_Shot02_StrongControl_00001_.mp4`

### 实验组 A：纯隐空间参考注入 (Pure Ref2VA)
- **底层架构**：纯 DiT 隐空间时空注入，完全断开 ControlNet
- **参数配置**：
  - 拔除 Node 48，Node 1 (`UNETLoader`) 直接连接 Node 7 (`BasicGuider`) 与 Node 9 (`BasicScheduler`)
  - 提示词显式增加近景贴身跟拍修饰
- **Prompt ID**：`44f4e586-142a-42c1-bd49-b6545994a7c7`
- **输出产物**：`StarCraft_Act01_Shot02_OptionA_PureRef.mp4`

### 实验组 B：ControlNet 降权与时间步退火 (Annealed ControlNet)
- **底层架构**：ControlNet Union 混合退火控制
- **参数配置**：
  - ControlNet 强度：降权至 `strength = 0.35`
  - 介入时间区间：`start_percent = 0.0, end_percent = 0.35`（退火机制：仅在前 35% 步数定下宏观体积与车体占位，后 65% 撤销约束）
- **Prompt ID**：`105dc61e-275e-4c9b-8e4a-0614fbf449f7`
- **输出产物**：`StarCraft_Act01_Shot02_OptionB_AnnealedControl.mp4`

---

## 2. 核心提示词（Prompt）

```text
StarCraft: Shadow of the Xel'Naga, Act I, shot 02. Use <Video 1> as the camera and blocking reference: preserve its intimate exterior low-angle side-rear tracking composition where the battered red industrial harvester fills the left half of the frame. Transform the whitebox into realistic live-action footage. <Picture 1> is the scene reference: match its distinctive battered red robo-harvester, storm-dark Bhekar Ro wheat fields, heavy clouds and violet lightning. A single industrial harvester races through muddy, wind-bent golden wheat under a violent storm, its treads throw wet mud and spray. A low side-tracking camera closely follows the vehicle continuously; no camera cuts, no cockpit interior, no visible people. Realistic 35mm anamorphic cinematography, dark steel blue and storm violet, rain and distant lightning. No subtitles, labels, watermarks, diagrams, UI or reference-sheet layout.
```

---

## 3. 验收标准

1. **白模构图咬合度**：是否还原低角度侧后方贴身跟拍（低模车尾占据画面左半部大部）；
2. **参考图替换成功率**：是否将参考图里的履带、液压臂、排气管与装甲板画出；
3. **几何伪影诊断**：是否存在直角粉红积木、纸盒人边缘或多边形闪烁。

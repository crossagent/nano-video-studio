# 工作流说明：3D 分镜时序切片驱动与多参考图视频生成

本工作流实现了**“以 3D 白模动态分镜为运镜/动作骨架，叠加多角色标准三视图与场景概念图生成高保真实拍级影视 Clip”**的工业管线。

---

## 节点拓扑与数据流向

1. **分镜视频输入与时序切片**：
   - `LoadVideo` (Node 22)：读取 `starcraft_previs_act01_unique_20261104.mp4`（33 秒总分镜预演）；
   - `VideoTemporalCrop` (Node 23)：输入 `start_frame: 144, length: 72`，精确提取 Shot 03 对应的 72 帧片段；
   - `GetVideoComponents` (Node 21)：解复用出 `IMAGE` 视频帧序列并连接至条件节点。
2. **多参考图注入**：
   - `LoadImage` (Node 19)：输入 `<Picture 1>` 拉尔斯·布伦角色设计大看板（包含三视图与特写）；
   - `LoadImage` (Node 24)：输入 `<Picture 2>` 奥克塔维亚·布伦角色设计大看板；
   - `LoadImage` (Node 26)：输入 `<Picture 3>` 场景 01 暴风麦浪与收割机概念大图。
3. **MiniMax H3 条件编码器 (`MiniMaxH3ReferenceToVideo`, Node 5)**：
   - 接收 Qwen-32B 文本/多模态特征，联合编码 `<Video 1>` 的镜头手持震颤/人物肢体动态与 `<Picture 1/2/3>` 的面部、服装、机械材质；
   - 提示词精确描述狭窄颠簸的收割机座舱、拉尔斯抓握操纵杆的亢奋神情、奥克塔维亚检查副驾仪表盘的警惕状态，窗外掠过的暴雨雷电；
   - 输出正向文本与图像/视频多模态条件 `CONDITIONING` 与初始化 `LATENT`。
4. **扩散采样与解码**：
   - `SamplerCustomAdvanced` (Node 10) + `BasicScheduler` (Node 9, Beta 20步) + `RandomNoise` (Node 8)；
   - `VAEDecode` (Node 11) + `VAEDecodeAudio` (Node 12)；
   - `CreateVideo` (Node 13, 24fps) + `SaveVideo` (Node 14)。

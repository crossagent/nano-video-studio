# 第一幕第一场 Seedance 原生 API 白模还原度对照任务

- **状态**：`review`（四镜 Seedance 候选已生成，待用户审阅资产与镜头。`S01-040` 旧样片详见 [`report.md`](report.md)）
- **主工具**：火山方舟 Doubao Seedance 2.5 API（`platform/seedance/client.py`）
- **辅助工具**：Blender 5.2.3 LTS（`platform/blender/run.cmd`）
- **目标**：验证在消除彩色色块渗漏、完成几何屏幕占比体检、并严格使用火山方舟原生 `role="reference_video"` + `role="reference_image"` + `参考@video1...` 规范的条件下，Seedance 2.5 原生 API 对第一场白模运镜与空间调度的 1:1 还原上限。
- **输入资产**：
  - 源工程：[`tasks/blender/act01-scene01-previs/work/act01_scene01_roadside_strike.blend`](../../blender/act01-scene01-previs/work/act01_scene01_roadside_strike.blend)
  - 外观参考图：[`assets/settings/scenes/scene-01-bhekar-ro-wheatfield-storm.jpg`](../../../assets/settings/scenes/scene-01-bhekar-ro-wheatfield-storm.jpg)
- **已准备就绪的本地前置产物**：
  - 中性纯灰白模工程：`work/act01_scene01_neutral_clay.blend`
  - 几何体检报告：`probe_report.json`
  - 分段与连贯中性白模视频（`1280×536`，24 fps，H.264 MP4）及首帧 PNG：`inputs/`
  - 预检通过的 480p 样片任务配置：`jobs/`
- **当前测试范围**：[`act01_scene01_roadside_strike_previs.mp4`](../../blender/act01-scene01-previs/output/act01_scene01_roadside_strike_previs.mp4) 的四个镜头，完整 18 秒、432 帧。依次为越脊俯冲、山脚落雷碎石、履带碾过碎石、收割机中景。该文件为带区分色的白模，纯中性灰完整四镜尚未导出。实际提交前核实模型和通道支持的输入与输出时长。
- **验收标准**：核对山口与山脊、俯冲路径、切镜顺序、雷击与碎石时点、履带接触和通过动作、车辆朝向及中景构图。当前白模用于检查场地和机位。麦穗连续倒伏、云雨推进如要严格跟随白模，需要先补入 Blender 动画。
- **其他对照**：`S01-040` 用于检查车辆占屏、朝向及跟拍。`S01-020–040` 用于检查落雷碎石、履带碾压与跨切。结果分别记录。

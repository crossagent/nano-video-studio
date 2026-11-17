# 复核流程

1. 以原著第一章为范围，对照第一幕剧本和文字分镜，识别关键动作、章节切点及镜号对应关系。
2. 使用 Blender 5.2.3 LTS 打开 `camera_fix` 工程，读取相机标记并检查九次切换前后的实际活动相机。

   ```powershell
   .\platform\blender\run.cmd --blend tasks/blender/act01-shared-world/work/act01_shared_world_camera_fix.blend --script tasks/blender/chapter01-storyboard-review/inspect_timeline.py
   ```

3. 用 FFmpeg 9.0.2 完整解码白模视频。将前七镜的第 4、36、71 帧抽出，按镜头各排一行存于 `work/chapter01-frame-grid.png`。与角色修订版的两张彩色分镜表对照，记录取景、连续动作和章尾覆盖情况。
4. 按正式文字分镜和白模各自的镜号记录结果，技术复核与原资产验收状态分别记录。

# Blender 准备及制作流程

1. 使用旧工程的收割机组作为来源，通过平台运行器构建独立的峡谷场地。`canyon_set.py` 定义地形及谷底布置。

   ```powershell
   .\platform\blender\run.cmd --blend tasks/blender/act01-shared-world/work/act01_shared_world_camera_fix.blend --script tasks/blender/act01-scene01-previs/setup_previs.py
   ```

2. 以 `shot-list.md` 校验四台相机、帧范围和反打朝向。在准备工程中用共用山口和尖峰串起前两镜。

   ```powershell
   .\platform\blender\run.cmd --blend tasks/blender/act01-scene01-previs/work/act01_scene01_canyon.blend --script tasks/blender/act01-scene01-previs/check_setup.py
   ```

3. 在场地版工程上运行 `render_canyon_preview.py`，生成 432 张工作帧。以 FFmpeg 按 24 fps 合成为 18 秒 H.264 MP4，验证完整解码、帧数和时长。
4. 雷击版以峡谷场地为输入，通过 `build_ridge_impact.py` 添加第 197 帧的落点、闪光及 34 个碎块，再由 `render_ridge_impact.py` 输出第 145–228 帧。FFmpeg 将新第二镜与场地版第 1–144、229–432 帧组合，附加第 8.167 秒起的临时雷声，并单独导出第二镜供对照。
5. 山脚落雷与履带版从 `act01_scene01_canyon.blend` 运行 `build_roadside_strike.py`。将可编辑碎片和右侧履带板放在同一条车辙。打开另存的 `act01_scene01_roadside_strike.blend` 运行 `render_roadside_strike.py -- samples` 抽查关键帧，运行同一脚本的默认模式输出第 145–432 帧。
6. FFmpeg 拼接原版第 1–144 帧与新输出的 288 帧，按 24 fps 输出 H.264 MP4。附加第 7.417 秒的临时雷声和第 10.630、10.935 秒的压碎音效。局部对照从全片 6 秒开始截取 8.5 秒。
7. 后续继续调校俯冲，制作麦浪倒伏和云与雨墙。待导演审阅后记录最终白模的版本与采用去向。

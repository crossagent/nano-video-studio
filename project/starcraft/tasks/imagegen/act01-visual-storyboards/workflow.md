# 工作流程与提示词

用内置 imagegen，以 10 张 Blender 抽帧按镜号分组作为各画格的构图参考，生成两张各包含 5 格的彩色分镜表。使用修复版驾驶舱和刀锋女王抽帧。提示要求电影感、工业科幻质感、保留机位与主要对象关系，画面细节依据剧本补充，不承诺严格复刻几何。

- 01–05：暴风雨中的麦原；红色履带收割机侧后；驾驶舱内左右两位布伦兄妹；低角度防空塔；板房工坊内兄妹与地震仪。
- 06–10：纸带地震仪特写；工坊地震；刀锋女王正面与骨翼；高角度神庙裂谷；人物正对巨大三角神庙门。

图 01–05 参考抽帧分别是 `shot_01_frame_001.png`、`shot_02_frame_073.png`、`camera_fix_0145.png`、`shot_04_frame_217.png`、`shot_05_frame_289.png`；图 06–10 分别是 `shot_06_frame_361.png`、`shot_07_frame_433.png`、`camera_fix_0545.png`、`shot_09_frame_577.png`、`shot_10_frame_673.png`，均在 `tasks/blender/act01-shared-world/output/checks/`。

角色修订版：以原分镜图为编辑目标，同时输入 assets/settings/characters/octavia-bren-full-sheet.jpg 与 lars-bren-full-sheet.jpg 为身份及服装参考；要求保留镜位、画格和其余画面，修改 03、05、07 的兄妹以及 10 的拉尔斯背影。使用内置 imagegen，输出 character_ref_v2，供对照审阅。

逐镜整理：使用 imagegen 去除分镜表编号，FFmpeg 裁出单格并从 camera_fix 预演视频逐帧切出 10 个视频；从原 PNG 序列拷贝每镜白模首帧。打包脚本为 package_shots.ps1；输出在 output/shots，含各镜的对齐限制。

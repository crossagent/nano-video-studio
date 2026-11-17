# MiniMax H3 白模与原始参考图验证

- 状态：review
- 目标：用 Seedance 实测时同一白模和两张参考图检验 MiniMax，不使用 Seedance 生成画面作为输入。
- 输入：`tasks/blender/act01-scene01-previs/output/act01_scene01_roadside_strike_previs.mp4` 18 秒；`tasks/seedance/act01-scene01-whitemodel-fidelity/inputs/style-canyon-wheat.jpg`；`tasks/seedance/act01-scene01-whitemodel-fidelity/inputs/style-harvester-material-580.jpg`。两张图与 Seedance 实际执行记录中的 SHA-256 一致。
- MiniMax 单次输入与输出限制要求按四镜拆分，沿用此前优化测试的 20 步、单镜提示和 608×256 输出。导出的视频为白模分段，尾部补帧适配 17n+5 帧数。
- 验收：检查镜头和动作、写实场景及车辆，重点比较既有 Seedance 参考帧方案和本次原始图方案。成片和对比仅作候选审阅。

# 工作流：Blender 3D Previs 预演执行流程

1. **环境安装与验证**：通过 Windows 官方包管理器静默安装 Blender 4.2 LTS，验证命令行 `blender -b -v`。
2. **自动化脚本编写**：编写无头执行 Python 脚本 `generate_act01_previs.py`，程序化构建：
   - 材质着色库（鲜明色块区分不同物体：麦原金、收割机樱桃红、装甲灰、神庙黑晶、能量亮蓝、查尔熔岩橙）；
   - 地形网格生成与空间体量布局；
   - 摄影机群组构建（匹配分镜脚本的景别与焦段）；
   - 动画与机位标记绑定。
3. **工程保存与渲染**：
   - 保存全场景至 `assets/storyboards/previs_act01_blocking.blend`；
   - 自动运行后台多机位视口渲染（Workbench/EEVEE），导出静帧至 `assets/storyboards/previs_renders/`。
4. **验证与交付**：检查各镜头画面构图是否准确传达导演分镜意图。

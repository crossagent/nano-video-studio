# Blender 3D 平台集成规范 (Platform Blender)

`platform/blender/` 负责管理影视工作室中所有与 **Blender 3D 引擎** 相关的调用逻辑、环境探测、自动化运行器及通用工具集。

---

## 一、架构职责分工

1. **平台层 (`platform/blender/`)**：
   - **环境抽象与定位**：自动探测本机安装的 Blender 5.x 版本或通过环境变量 `BLENDER_PATH` 定位；
   - **统一调用工具**：提供统一的执行入口 `run.ps1`，封装无头后台运行（`-b`）、Python 脚本注入与参数映射；
   - **通用影视预演库**：提供 `previs_toolkit.py`，预置 2.39:1 宽银幕画幅规范、Workbench 高对比度视口、摄像机矩阵与快照导出接口。

2. **任务层 (`tasks/blender/<task-id>/`)**：
   - **任务独立存储**：每一次具体的 3D 建模、分镜预演（Previs）、相机调度、灯光或毛坯搭建任务，均必须独立存放在 `tasks/blender/<task-id>/` 下；
   - **任务目录结构**：
     - `task.md`：任务目标、输入依赖、交付目标；
     - `workflow.md`：执行流程、镜头清单、参数规范；
     - `log.md`：执行日志与评审记录；
     - `scene_build.py`：本任务专属的场景构建与调度脚本；
     - `work/`：过程工程文件（`.blend` 草稿或几何缓存）；
     - `output/`：最终交付的视口渲染快照（PNG）或正式工程。

3. **资产入库层 (`assets/storyboards/`)**：
   - 任务验收通过后的正式成果，发布至资产目录（如 `assets/storyboards/previs_act01_blocking.blend`）。

---

## 二、平台统一调用方式

在 PowerShell 终端中调用 `platform/blender/run.ps1`：

```powershell
# 1. 运行任务专有 Python 脚本（默认无头后台执行）
.\platform\blender\run.ps1 -Script "tasks/blender/previs-blocking-act-001/build_previs.py"

# 2. 指定加载某个 .blend 文件并运行检查脚本
.\platform\blender\run.ps1 -BlendFile "assets/storyboards/previs_act01_blocking.blend" -Script "tools/check_scene.py"

# 3. 传递自定义参数给 Python 脚本（脚本内通过 sys.argv[sys.argv.index('--') + 1:] 接收）
.\platform\blender\run.ps1 -Script "tasks/blender/my-task/build.py" -- -Shot "Shot01" -Quality "High"
```

---

## 三、通用预演工具库 (`previs_toolkit.py`)

在 `tasks/blender/<task-id>/` 下的脚本中，可以直接导入平台工具库：

```python
import sys
sys.path.append(r"D:\nano-video-studio\platform\blender")
import previs_toolkit as ptk

# 1. 一键初始化 2.39:1 宽银幕 Previs 场景
ptk.init_previs_scene(width=1920, height=804)

# 2. 快速创建标准着色材质
mat_red = ptk.create_previs_material("Mat_Red", (0.8, 0.1, 0.1, 1.0))

# 3. 构建指定焦距摄影机
cam = ptk.create_previs_camera("Camera_Shot01", location=(0, 20, 2), rotation_deg=(85, 0, 180), focal_length=24.0)

# 4. 批量导出各摄像机快照
ptk.render_camera_snapshots(cameras_dict, output_dir="output/")
```

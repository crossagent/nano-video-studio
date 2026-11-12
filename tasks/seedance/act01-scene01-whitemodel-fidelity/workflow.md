# 制作与测试流程

## 一、本地零消耗准备流程（已完成）

1. **中性纯灰 Clay 白模转换与几何体检**：
   ```powershell
   .\platform\blender\run.cmd --blend tasks/blender/act01-scene01-previs/work/act01_scene01_roadside_strike.blend --script tasks/seedance/act01-scene01-whitemodel-fidelity/prepare_whitemodel.py
   ```
   - 将原工程的高饱和色块（樱桃红车身、亮青玻璃、明黄顶灯、橙/蓝双色驾驶员及死黑履带）统一替换为分层中性灰 Clay（Saturation = 0.0），消除颜色渗漏风险；
   - 开启 Blender Workbench `STUDIO` 光照、`Cavity (BOTH)` 与投影，背景设为亮灰阴天 `(0.74, 0.74, 0.74)`，温和化第 179 帧闪电曝光峰值（上限 `0.35`）；
   - 自动按分镜拆段输出 `1280×536`（2.39:1）24 fps H.264 MP4 及首帧对照 PNG，并生成屏幕占比体检报告 `probe_report.json`。

2. **原生 API 离线校验与预演（零消耗）**：
   ```powershell
   & "C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" platform/seedance/client.py validate tasks/seedance/act01-scene01-whitemodel-fidelity/jobs/job_s01_040_benchmark_480p.json
   & "C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" platform/seedance/client.py submit tasks/seedance/act01-scene01-whitemodel-fidelity/jobs/job_s01_040_benchmark_480p.json --dry-run
   ```

## 二、后续额度实测步骤（待授权 Key 后执行）

1. **配置鉴权与接入点**：
   ```powershell
   $env:ARK_API_KEY = "您的火山方舟 API Key"
   # 若需指定实际接入点 Endpoint ID，可修改 jobs/*.json 中的 model 字段或设置：
   # $env:SEEDANCE_MODEL = "ep-xxxxxxxx"
   ```
2. **先跑主基准单镜 480p 样片（省额度验证运镜）**：
   ```powershell
   & "C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" platform/seedance/client.py run tasks/seedance/act01-scene01-whitemodel-fidelity/jobs/job_s01_040_benchmark_480p.json
   ```
3. **对照验证结果**：
   - 检查 `output/` 下回传 MP4 的运镜与主体轨迹；
   - 若单镜刚体跟拍 1:1 达标，再依次执行 `job_s01_010_canyon_dive_480p.json`（纯相机俯冲）与 `job_s01_020_040_roadside_strike_480p.json`（落雷碎石多切段）。

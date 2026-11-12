# 执行记录

## 1. 本地零消耗准备完成（2026-11-10）

### 平台接口与客户端 (`platform/seedance/`)
- 新增火山方舟 Seedance 原生异步任务客户端 [`platform/seedance/client.py`](../../../platform/seedance/client.py)（基于 Python 3.13 标准库，零第三方依赖），支持 `validate`、`upload`、`submit --dry-run`、`collect` 和 `run`。
- 已通过单元测试（[`platform/seedance/tests/test_client.py`](../../../platform/seedance/tests/test_client.py)，3 项测试全部通过）。

### 中性纯灰白模资产制备 (`inputs/` & `work/`)
- 以 [`act01_scene01_roadside_strike.blend`](../../blender/act01-scene01-previs/work/act01_scene01_roadside_strike.blend) 为源工程，运行 [`prepare_whitemodel.py`](prepare_whitemodel.py) 输出无损中性灰工程 `work/act01_scene01_neutral_clay.blend`。
- 消除了原工程的高饱和色块（樱桃红车身、亮青挡风玻璃、明黄顶灯、橙/蓝驾驶员占位及死黑履带），统一映射为分层纯中性灰（`Saturation = 0.0`），开启 Workbench `STUDIO` 光照、`Cavity (BOTH)` 与投影，温和化第 179 帧闪电过曝峰值（上限 `0.35`）。
- 使用 Blender 5.2.3 LTS 内置 FFmpeg H.264 编码器导出 5 段干净白模视频（`1280×536`，24 fps，`yuv420p`）及对应首帧 PNG，并完成流信息核验：
  - `inputs/s01_010_clay.mp4`：6.00s（144 帧，1,010,793 字节）— 山脊俯冲纯运镜
  - `inputs/s01_020_clay.mp4`：3.50s（84 帧，453,283 字节）— 山脚落雷碎石
  - `inputs/s01_030_clay.mp4`：3.00s（72 帧，354,608 字节）— 右履带近景碾压碎石
  - `inputs/s01_040_clay.mp4`：5.50s（132 帧，774,813 字节）— 收割机侧后跟拍（主基准）
  - `inputs/s01_020_040_clay.mp4`：8.50s（204 帧，1,112,664 字节）— 连续落雷碾压跨切动作段

### 几何与屏幕占比体检 (`probe_report.json`)
- `s01_010`（通过）：纯相机大场景俯冲调度，依赖山脊与麦垄连续纹理提供光流梯度。
- `s01_020`（通过）：岩石主体屏幕宽度占比 `54.1%`，无截断。
- `s01_030`（触发提示）：由于机位蹲守车辙近景等待车体进入，首尾帧车体处于画外（`0.0%`），中段履带占宽 `73.4%` 并裁边；该镜适合作为后续多切连续段验证，不建议作单镜首轮盲测基准。
- `s01_040`（通过）：收割机连续占据 `86.5%` 屏幕宽度，与刚体跟车基准场景匹配度最高，定为首轮 `480p` 样片测试主基准。

### 离线任务校验（零额度消耗）
- 对 `jobs/job_s01_040_benchmark_480p.json`、`jobs/job_s01_010_canyon_dive_480p.json`、`jobs/job_s01_020_040_roadside_strike_480p.json` 执行 `client.py validate`，以及对 `job_s01_040_benchmark_480p.json` 执行 `client.py submit --dry-run`，均校验通过（`"valid": true`，`"warnings": []`）。

## 2. OpenRouter `bytedance/seedance-2.5` 首轮实测结果（2026-11-10）

- **任务配置**：[`jobs/job_openrouter_s01_040_480p.json`](jobs/job_openrouter_s01_040_480p.json)
- **模型**：`bytedance/seedance-2.5`（`480p` / `992×432`、`21:9`、`24 fps`、`6s`、`generate_audio: false`）
- **输入组合**：`input_references` 传入 `scene-01-bhekar-ro-wheatfield-storm.jpg`（Base64）与 `s01_040_clay.mp4`（临时 HTTPS 直链 `https://n.uguu.se/WzzERQZM.mp4`）
- **任务 ID**：`gen-vid-1794304745-qM14l6Vw9BxYbJU7yilq`（上游任务 `cgt-20261110175910-jdrma`）
- **实际费用**：`$0.7097728`，与含视频参考计费档位相符。执行记录未保存上游获取的视频内容或实际帧使用情况。
- **成片文件**：`runs/openrouter-s01-040-480p/output/openrouter-s01-040-480p_openrouter.mp4`（`992×432`、24 fps、6.04s）
- **人工抽帧视觉核验结论（未达到 1:1 还原）**：
  - 成片 00:00~00:05 几乎完全照搬了场景参考图 `scene-01-bhekar-ro-wheatfield-storm.jpg` 的大远景构图（收割机位于右下角且车头朝左前方、远景山脊与麦浪固定不动），仅对麦浪、泥点和闪电做了微幅局部动态；
  - 彻底忽略了 `s01_040_clay.mp4` 的侧后方近景贴车构图（占宽 `86.5%`、车头朝右行驶的跟拍运镜）。
  - **关键归因**：整幅参考图与白模视角冲突，成片首帧接近参考图，支持图像构图主导的推断。下一步需做纯白模与同视角参考图的对照。

## 3. 本地证据复核（2026-11-10）

- 重新完整解码白模和生成视频，分别为 132 帧与 145 帧。核对当前 JPG 的 SHA-256 与执行记录一致，并比对首帧、主体尺度、行驶方向和背景视差。
- 计费记录只用于核对费用。素材摘要没有上游视频字节或帧使用记录。方舟原生显式编辑与 OpenRouter 的参考输入区分记录，复核未提交生成任务。

## 4. 用户确认测试镜头（2026-11-10）

- 用户指定 `S01-010`，从山脊俯冲到麦田。原试验把画面占比易于量化的 `S01-040` 定为主基准，实际只回传了这一镜的样片。
- 抽查 `S01-010` 独立白模的第 1、49、97、144 帧。从山口高处俯瞰谷地，中段掠过山脊并下滑，末段贴近谷底麦垄。已有 `S01-010` 配置仍带包含收割机的场景概念图，纯白模基线应去掉该图及提示词引用。未提交新样片。

## 5. 用户扩展为四镜（2026-11-10）

- 用户要求包含俯冲、石头被劈碎、履带碾压和车辆中景。核对 Blender 完整预演 `output/act01_scene01_roadside_strike_previs.mp4`，该候选为 18 秒四镜，抽查四镜画面确认覆盖要求。当前测试范围改用完整候选，生成通道和时长尚待验证。

## 6. 四镜提示词与素材准备（2026-11-10）

- 准备 `jobs/job_openrouter_s01_full_480p.json` 和 `inputs/s01-full-reference-notes.md`，指定 18 秒白模、四镜事件与两个材质裁图。裁图来自已存场景概念图，作为风格参考。
- 方舟原生视频编辑支持 4–30 秒输入，输出时长可能比输入短最多 0.4 秒。OpenRouter 的模型介绍与通用接口文档对 Seedance 2.5 视频参考的支持表述存在差异，待验证实际通道。未提交生成。

## 7. 明确白模视频生成方向（2026-11-10）

- 用户明确要求以粗糙白模视频控制时间线和镜头，以预制环境、角色与场景参考图控制外观。补充调研 `layout-to-video-research.md`，记录 Seedance 2.5 白模参考渲染和 LTX-2.5 Layout to Render 的输入及实际限制。此前准备的局部材质参考仅为候选，不视作完整角色或场景参考。

## 8. 四镜 Seedance 生成（2026-11-10）

- 按用户要求提交 18 秒完整 `act01_scene01_roadside_strike_previs.mp4`，白模摘要 SHA-256 为 `9a2202015d21ab3f8318f68e7c068b62e2b7301aa21af3a3bfc0eba156874e3a`。使用场景局部裁图和收割机红漆局部裁图，两张均作为外观参考。
- 初次提交被 HTTP 400 拒绝，服务提示车辆参考图 290×200 低于 90000 像素要求。将该图放大至 580×400 后重试。放大不增加原图细节。
- OpenRouter 接收任务 `gen-vid-1794312727-mHre57zlcwRazJmnxivz`。完整任务配置在 `jobs/job_openrouter_s01_full_480p_submit.local.json`，执行与回收记录保存在 `runs/openrouter-s01-full-480p/`。
- 该任务异步失败，返回模型将提示词识别为视频编辑，需要 `ratio=adaptive` 和 `duration=-1`。随后将开头改为白模参考生视频，保留 18 秒与 21:9，另建任务 `gen-vid-1794313048-B4aU245fA4FU0cETLqDK`。
- 第二个任务完成，实际记录费用 2.3168128 美元。成片位于 `runs/openrouter-s01-full-reference-480p/output/openrouter-s01-full-reference-480p_openrouter.mp4`，完整解码 433 帧、24 fps、992×432，约 18.04 秒，无音轨。抽帧可见峡谷俯冲、岩石碎裂、履带与碎石、红色车辆。碎石发出橙色熔岩般光亮，车辆造型和逐帧接触仍待用户审阅。
- 按同帧号抽查 10 对画面，生成 `output/comparison_full.jpg` 和 `output/comparison.md`。抽查支持主要镜头与事件近似跟随，不能证明逐帧一致。


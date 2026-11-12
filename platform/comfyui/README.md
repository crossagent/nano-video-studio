# 本地 ComfyUI

图形界面用于搭建、单次调试工作流；Codex 使用同一实例的 API 批量执行。无需额外平台服务。脚本使用 Node.js 22 或更新版本，无第三方依赖。

## 连接

先通过现有 ComfyUI Desktop 或启动器启动实例。默认地址为 http://127.0.0.1:8188；若桌面版使用其他端口，在当前终端设置：

```powershell
$env:COMFYUI_URL = 'http://127.0.0.1:8188'
node platform/comfyui/client.mjs status
Start-Process $env:COMFYUI_URL
```

唯一部署方案为已有 Comfy Desktop；本工程不会安装第二份 ComfyUI。安装目录和端口不绑定，连接地址以实际启动界面为准。两边不共享 Python 环境、依赖或 Git 仓库，本工程不向 custom_nodes 写入任何文件。调试与批量使用同一个 HTTP 服务和队列，调试时应避免同时提交大批任务。

维护隔离不等于 API 永不变化：ComfyUI 更新后先对已登记工作流做单任务回归，再开批次；客户端在提交前检查节点类型是否存在，但模型兼容性和执行行为仍以实际试跑为准。nano-agent 升级只改本工程，不触碰桌面版安装。

## 在图形界面使用资产

```powershell
node platform/comfyui/client.mjs sync-assets
```

将 assets 内 PNG、JPEG、WebP 通过 /upload/image 导入运行实例。原生 LoadImage 在刷新节点选项或重开工作流后可选择 studio- 前缀文件。路径和内容共同决定文件名；映射写入 assets.local.json，其中 image 字段也可直接用于 API 工作流的图片输入。

这是资产快照，ComfyUI 对输入的操作不会修改正式资产。资产改变后重新同步。不会自动清理旧快照，以免破坏已保存工作流。视频、音频输入因自定义节点接口不同，按对应节点要求配置，不使用这个图片同步命令。

## 图形调试 → Codex 批量执行

1. 在图形界面调试生图或生视频工作流。
2. 导出 API 格式节点图，保存到 workflows/<名称>.api.json。普通界面 JSON 含 nodes/links，不能直接提交 /prompt；若界面没有 API 导出入口，先在设置中启用开发者选项。
3. 同目录保存工作流说明，记录模型、自定义节点、版本与可覆盖的节点输入。图形编辑版可保存为 <名称>.ui.json。
4. 参照 batch.example.json 创建批次，每个 job 是一个独立任务。inputs 以节点 ID 映射需要覆盖的输入；图片名称可从 assets.local.json 取得。批次中应使用不同 seed 或其他明确参数控制变化。
5. Codex 直接运行以下命令提交与收集：

```powershell
node platform/comfyui/client.mjs submit platform/comfyui/batch.local.json
node platform/comfyui/client.mjs collect video-shot-001
```

submit 顺序入队后立即返回，不等待 GPU 执行结束。collect 查询一次历史；尚未完成时稍后再调用。脚本保存实际提交的完整工作流、输入覆盖、prompt_id、历史与输出清单，结果下载到 `tasks/comfyui/<task-id>/output/`。collect 也能读取此前放在 `tasks/<task-id>/` 的记录。任务文档保留要求、流程和执行记录，验收后由 Codex 将采用结果归入 assets。

网络中断后不自动重提，避免重复消耗 GPU；查看任务 submission.json 与 ComfyUI 队列确认。已存在的任务目录拒绝重复提交。批次部分提交失败时，保留成功任务，只为剩余任务另建批次。

## 命名参数与直接引用资产

将调试好的 API 图与 `.definition.json` 一起保存在 `workflows/`。definition 的 bindings 把 prompt、seed、reference 等名字映射到节点输入，只有工作流维护者需要关心节点 ID。`workflow.example.json` 是绑定格式示例，节点 ID 必须与实际图一致。defaults 提供默认参数，job.parameters 覆盖默认值，旧版 job.inputs 仍可覆盖具体节点。

例如图中有 LoadImage，给它的 image 输入绑定 reference 后，批次任务可这样写：

```json
{
  "task": "video-shot-003",
  "parameters": {
    "prompt": "人物转头看向窗外",
    "seed": 42,
    "reference": { "asset": "assets/settings/characters/hero-v1.png" }
  }
}
```

批量执行会自动上传被引用的图片，无需手抄同步后的文件名。上传是内容快照，不是目录挂载，原始资产不受 ComfyUI 修改影响。每项任务的 execution.json 记录实际引用图片的 SHA-256、上传名称、连接地址、工作流定义与服务版本；workflow.json 是实际提交图。收集时要求使用原服务地址。

完整批量运行（提交、等待、下载）只需一条命令：

```powershell
node platform/comfyui/client.mjs run platform/comfyui/minimax.batch.example.json
```

这个示例使用已下载的 MiniMax H3 模型，包含两个文生视频任务，会实际占用 GPU。默认最多等待 6 小时，可用 timeoutSeconds 调整；超时不取消服务端任务，稍后用 collect 收集。单项生成失败时仍继续收集其余任务，最后返回失败信息。网络错误会保留任务记录，可恢复 collect；不会自动重复提交。示例任务 ID 使用一次后必须更换。

图形调试版 `minimax-h3.ui.json` 与 API 执行版分别维护，修改图形图后必须重新导出 API 图并检查绑定；不会从正在编辑且未导出的界面中读取工作流。当前 MiniMax 示例不包含参考图片输入；不要将 reference 参数直接加到该图。

生图和生视频使用相同的图执行 API，模型及算法由工作流决定。原生图片输出和返回 filename/subfolder/type 文件描述的视频输出可自动收集；自定义节点未返回此描述时，需要按其接口补充收集逻辑，不能保证所有插件通用。

## 角色参考（Ref2VA）

桌面版工作流列表中的 `MiniMax-H3-Character-Reference` 提供人物图片入口。先在 LoadImage 上传角色图片，再在提示词中用 `<Picture 1>` 指定该人物，并描述新场景、动作和声音。参考约束会影响外观，但不保证跨镜头身份完全一致，需要评审结果。该图没有固定首帧的要求。

工程对应文件为 `workflows/minimax-h3-reference.ui.json`、`.api.json` 和 `.definition.json`；批量示例 `character-reference.batch.example.json`。将示例 reference.asset 替换为真实资产路径，提示词中保留 `<Picture 1>`。

它使用独立的 `minimax_h3_ref2va_pruned_int8_convrot.safetensors` 主权重，复用已有文本编码器和两个 VAE，标准 20 步，不依赖 FL2V 或 Ref2V 加速 LoRA。默认 608×352、56 帧约 2.3 秒、ref_image_size=match，作为低分辨率调试起点。尚未用实际角色图跑过生成。

主权重可用 `python platform/comfyui/download-reference-model.py <桌面版共享models目录>` 下载并校验。该脚本仅下载官方 Ref2VA 单个文件，不安装或更新 ComfyUI；支持断点续传，完成 SHA-256 校验后才启用正式文件名。图形工作流中如看不到新模型，刷新节点选项后再选择。

## 白模转写实工作流与生成规则（已验证方案）

针对“3D 灰白模动态分镜（Previs）转实拍级视频”任务，目前已验证两套正确可用方案，本地 ComfyUI 侧采用第 4 版方案（`workflows/minimax-h3-previs-firstframe.api.json` + `.definition.json`）：

- **第 4 版方案结构（独立对齐首帧 + `MiniMaxH3AddGuide` + `Ref2VA`）**：
  1. 用白模第 0 帧结合美术风格参考图，预先独立生成一张与白模构图、机位和焦段严格对齐的写实首帧（`<Picture 1>`）。
  2. 将该首帧同时接入 `MiniMaxH3ReferenceToVideo.ref_images.ref_image_0` 与 `MiniMaxH3AddGuide(frame_idx=0)`，把第 0 帧写实质感硬锚定到视频时间轴起点。
  3. 仅输入单镜白模 `<Video 1>`（经 `VideoTemporalCrop` + `GetVideoComponents` 提取帧序），经 `BasicGuider`（`res_multistep` + `beta` + `denoise=1`）联合采样并输出 24 fps 音视频。
- **已验证 5 条核心生成规则**：
  1. **必须使用标准 20 步基础采样，禁用 4 步 Turbo LoRA**：实测 4 步 Turbo LoRA 会导致高比例灰白模残留与大面积色块模糊；必须使用 `minimax_h3_ref2va_pruned_int8_convrot.safetensors` 原生 20 步（`steps=20`）。
  2. **按单镜拆分且帧长严格对齐 `17n+5`**：禁止多镜拼接长视频整段直出（会引发跨镜风格崩坏）；每段按 `5, 22, 39, 56, 73, 90, 107, 124, 141, 158...`（即 `17n+5`）对齐，末尾不足时在白模切片阶段用尾帧补齐，成片后再裁回原帧数（例如 158 帧生成后裁回 144 帧）。
  3. **必须使用结构化 Ref2VA 提示词框架**：包含 `subject_definitions`、`summary`、`retention_analysis`（`<Video 1>` 标注 `fully_preserved`，`<Subject 1>` 标注 `attribute_transfer`）、`detailed_description`、`overall_soundscape`、`non_diegetic_music`，避免空泛英文自然段导致模型忽略白模约束。
  4. **写实首帧裁剪与构图必须与白模第 0 帧 1:1 对齐**：不要擅自补充额外天空、留白或拉远景别，否则 `AddGuide(frame_idx=0)` 会拖慢前段俯冲节奏约 0.8–1.0 秒。
  5. **参考图最小化与朝向一致性检查**：每镜只传入该镜头真实出镜的参考图（如纯峡谷俯冲镜禁止挂入 `<Picture 2>` 收割机），若参考角色/载具存在明确朝向，需确保参考图朝向与白模一致（否则 `Ref2VA` 会按参考图朝向反向翻转白模实体；复杂多角度重投影需求可改用云端 `platform/seedance/` 方案）。

## 本地环境与排障说明

本机实测（RTX 5060 Ti 16 GB 显存 + 32 GB 内存，Windows + ComfyUI Desktop）发现以下环境约束，均保留在本地运行配置中，**不纳入 Git 版本库**：

1. **显存与 `--lowvram` 启动要求**：`minimax_h3_ref2va` 与 `qwen3vl_32b` 编码器合计约 35 GB 权重，16 GB 显存直接默认模式易触发 OOM，本地命令行启动需附加 `--lowvram`；实测 `608×256` 分辨率、20 步采样下，73–90 帧约 12–24 分钟，158 帧约 53–59 分钟（约 159 秒/步）。
2. **ComfyUI Desktop `--extra-model-paths-config` 失效兜底**：脱离桌面版托盘直接无头启动后端时，`AppData\Roaming\Comfy Desktop\instance-model-paths\inst-*.yaml` 可能因实例 ID 变化或清理而失效，可在本地新建被 Git 忽略的 `models.local.yaml`，显式指向本机共享 `models/` 目录（`diffusion_models`、`text_encoders`、`vae`、`loras`）。
3. **Windows 下 Python / Node / FFmpeg 路径**：系统默认 `python`/`python3` 可能命中 Microsoft Store 占位符；本地自动化优先调用 ComfyUI 虚拟环境 `.venv\Scripts\python.exe`（内含 `imageio_ffmpeg` 可用于裁切与拼合对比视频）或 Blender 自带 `python.exe`。
4. **ComfyUI `/history` 输出字段差异**：`SaveVideo` 节点在 `/history/{prompt_id}` 返回中位于 `outputs[node_id].images`（附带 `"animated": [true]` 标记），而非 `videos` 字段，归档脚本需按此读取。
5. **安装包与权重外置**：ComfyUI 安装目录、安装包、本地运行日志（`*.local.log`）、本地配置（`*.local.yaml` / `*.local.json`）及全部 `.safetensors` 权重文件严格禁止提交至 Git，由 `.gitignore` 统一隔离。

## 测试命令

```powershell
node --test platform/comfyui/tests/*.test.mjs
```

本地文件测试无需 ComfyUI 或 GPU。实际生成需要运行实例、已安装模型以及用户调试好的工作流。

# 火山引擎 Doubao Seedance API 接入

`platform/seedance/` 封装火山方舟（Volcengine Ark）视频生成异步任务接口，面向 **Blender 白模视频（`reference_video`）+ 写实参考图（`reference_image` / `first_frame`）** 的双轨还原工作流。脚本使用纯 Python 3 标准库实现（零第三方依赖），可直接由本机 Blender 内置 Python 3.13 运行。

---

## 一、运行环境与鉴权

```powershell
$env:ARK_API_KEY = "您的火山方舟 API Key"
# 可选：覆盖接入点/模型 ID 或区域地址
# $env:SEEDANCE_MODEL = "ep-xxxxxxxx"
# $env:ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
```

本机零配置运行入口（使用 Blender 5.2 自带 Python 3.13）：

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" platform/seedance/client.py --help
```

---

## 二、常用命令

### 1. 离线校验与预演（零消耗）

检查任务 JSON 合法性、本地媒体文件存在性与 SHA-256，以及提示词占位符（`参考@video1`、`reference_image` 等）是否规范：

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" platform/seedance/client.py validate path/to/job.json
& "C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" platform/seedance/client.py submit path/to/job.json --dry-run
```

### 2. 提交并等待下载成片

> 首次验证运镜一致性建议使用 `"resolution": "480p"` 样片模式降低额度消耗，确认运镜 1:1 贴合后再切换 `"1080p"`。

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" platform/seedance/client.py run path/to/job.json
```

* 本地图片（`<= 4MB`）默认转为小写格式 Data URI（`data:image/jpeg;base64,...`），也可通过 `--upload-images` 强制走 Files API。
* 本地白模视频默认通过火山方舟 Files API（`POST /api/v3/files`，`purpose=user_data`）自动上传并引用 `file_id://...`（若资产中已直接填写 `https://` 或 `tos://` 则跳过上传）。
* 提交后会在 `task_dir` 写入 `submission.json` 与 `execution.json`，并禁止重复提交（防止误刷额度）。
* 生成完成后自动拉取 `history.json`、`outputs.json` 并下载 MP4 到 `<task_dir>/output/`。

### 3. 单独查询/收集已有任务

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" platform/seedance/client.py collect tasks/seedance/<task-id> --wait
```

---

## 三、测试命令

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" -m unittest discover -s platform/seedance/tests -v
```

---

## 四、OpenRouter `/api/v1/videos` 通道（`openrouter_client.py`）

除火山方舟直连外，[`openrouter_client.py`](openrouter_client.py) 支持通过 OpenRouter 统一视频接口调用 `bytedance/seedance-2.5`、`bytedance/seedance-2.0` 与 `bytedance/seedance-2.0-mini`（无需 200 元余额门槛）：

```powershell
# 在 .env 配置 OPENROUTER_API_KEY=sk-or-...
& "C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" platform/seedance/openrouter_client.py validate tasks/seedance/act01-scene01-whitemodel-fidelity/jobs/job_openrouter_s01_040_480p.json
& "C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" platform/seedance/openrouter_client.py run tasks/seedance/act01-scene01-whitemodel-fidelity/jobs/job_openrouter_s01_040_480p.json
```


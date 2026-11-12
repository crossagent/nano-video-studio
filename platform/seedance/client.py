"""
platform/seedance/client.py
火山引擎火山方舟（Volcengine Ark）Doubao Seedance 视频生成平台通用客户端。
使用 Python 3 标准库实现（零第三方依赖），可由本机 Blender Python 3.13 直接执行。
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
REPO_ROOT = Path(__file__).resolve().parents[2]


def load_repo_dotenv() -> dict[str, str]:
    dotenv_path = REPO_ROOT / ".env"
    parsed: dict[str, str] = {}
    if not dotenv_path.exists():
        return parsed
    for raw_line in dotenv_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key:
            parsed[key] = val
    return parsed


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_repo_path(raw_path: str, base_dir: Path | None = None) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    if base_dir is not None:
        rel_to_job = (base_dir / candidate).resolve()
        if rel_to_job.exists():
            return rel_to_job
    return (REPO_ROOT / candidate).resolve()


def encode_image_data_uri(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    if ext == "jpg":
        ext = "jpeg"
    if ext not in {"png", "jpeg", "webp", "bmp"}:
        mime, _ = mimetypes.guess_type(str(path))
        ext = (mime or "image/png").split("/")[-1].lower()
    raw = path.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:image/{ext};base64,{encoded}"


def get_api_key(explicit_key: str | None = None) -> str:
    dotenv = load_repo_dotenv()
    key = (explicit_key or os.environ.get("ARK_API_KEY") or dotenv.get("ARK_API_KEY") or "").strip()
    if not key:
        raise RuntimeError(
            "未检测到 ARK_API_KEY。请在项目根目录 .env 配置 ARK_API_KEY，设置环境变量，或先使用 --dry-run / validate 验证本地配置。"
        )
    return key


def http_json_request(
    method: str,
    url: str,
    api_key: str,
    payload: dict[str, Any] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} 调用 {url} 失败: {detail}") from exc


def http_multipart_upload(
    url: str,
    api_key: str,
    file_path: Path,
    purpose: str = "user_data",
    timeout: int = 300,
) -> dict[str, Any]:
    boundary = f"----SeedanceBoundary{uuid.uuid4().hex}"
    mime_type, _ = mimetypes.guess_type(str(file_path))
    mime_type = mime_type or "application/octet-stream"
    file_bytes = file_path.read_bytes()

    parts = [
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="purpose"\r\n\r\n'
        f"{purpose}\r\n".encode("utf-8"),
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"),
        file_bytes,
        f"\r\n--{boundary}--\r\n".encode("utf-8"),
    ]
    body = b"".join(parts)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} 上传 {file_path} 失败: {detail}") from exc


def upload_file_to_ark(
    base_url: str,
    api_key: str,
    file_path: Path,
    purpose: str = "user_data",
    wait_ready: bool = True,
    timeout_sec: int = 180,
) -> dict[str, Any]:
    files_url = f"{base_url.rstrip('/')}/files"
    result = http_multipart_upload(files_url, api_key, file_path, purpose=purpose)
    file_id = result.get("id")
    if wait_ready and file_id:
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            status = str(result.get("status", "")).lower()
            if status in {"processed", "active", "ready", "succeeded"}:
                break
            if status in {"failed", "error"}:
                raise RuntimeError(f"文件 {file_id} 服务端处理失败: {result}")
            time.sleep(3)
            result = http_json_request("GET", f"{files_url}/{file_id}", api_key)
    return result


def load_job(job_path: Path) -> dict[str, Any]:
    data = json.loads(job_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"任务配置必须是 JSON 对象: {job_path}")
    return data


def build_payload_and_audit(
    job: dict[str, Any],
    job_dir: Path,
    dry_run: bool = True,
    base_url: str = DEFAULT_BASE_URL,
    api_key: str | None = None,
    upload_images: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    dotenv = load_repo_dotenv()
    model = os.environ.get("SEEDANCE_MODEL") or dotenv.get("SEEDANCE_MODEL") or job.get("model") or ""
    if not model:
        raise ValueError("job.json 缺少 'model'（例如 doubao-seedance-2-5-xxxxxx 或接入点 ID）。")

    items = job.get("content")
    if not isinstance(items, list) or not items:
        raise ValueError("job.json 必须包含非空 'content' 数组。")

    resolved_content: list[dict[str, Any]] = []
    asset_audit: list[dict[str, Any]] = []
    warnings: list[str] = []

    has_ref_video = False
    has_ref_image = False
    prompt_texts: list[str] = []

    for idx, item in enumerate(items):
        item_type = item.get("type")
        if item_type == "text":
            text = str(item.get("text", "")).strip()
            if not text:
                raise ValueError(f"content[{idx}] text 不能为空。")
            prompt_texts.append(text)
            resolved_content.append({"type": "text", "text": text})
            continue

        if item_type in {"image_url", "video_url"}:
            media_obj = dict(item.get(item_type, {}))
            role = item.get("role")
            if item_type == "video_url":
                has_ref_video = True
                if role != "reference_video":
                    warnings.append(f"content[{idx}] 为 video_url，建议显式设置 role='reference_video'。")
            if item_type == "image_url":
                has_ref_image = True
                if role not in {"reference_image", "first_frame", "last_frame"}:
                    warnings.append(
                        f"content[{idx}] 为 image_url，建议显式设置 role='reference_image' 或 'first_frame'。"
                    )

            url_val = media_obj.get("url", "")
            asset_ref = item.get("asset") or media_obj.get("asset")
            if asset_ref:
                local_path = resolve_repo_path(asset_ref, job_dir)
                if not local_path.exists():
                    raise FileNotFoundError(f"找不到本地资产文件: {local_path}")
                size_bytes = local_path.stat().st_size
                digest = sha256_file(local_path)

                audit_entry = {
                    "index": idx,
                    "type": item_type,
                    "role": role,
                    "asset": str(local_path.relative_to(REPO_ROOT)).replace("\\", "/")
                    if local_path.is_relative_to(REPO_ROOT)
                    else str(local_path),
                    "size_bytes": size_bytes,
                    "sha256": digest,
                }

                if dry_run:
                    url_val = f"<dry-run:{local_path.name};bytes={size_bytes};sha256={digest[:12]}>"
                    audit_entry["transport"] = "dry-run"
                else:
                    if item_type == "image_url" and not upload_images and size_bytes <= 4 * 1024 * 1024:
                        url_val = encode_image_data_uri(local_path)
                        audit_entry["transport"] = "data-uri-base64"
                    else:
                        if not api_key:
                            raise RuntimeError("需要 API Key 上传本地媒体文件。")
                        upload_resp = upload_file_to_ark(base_url, api_key, local_path)
                        file_id = upload_resp.get("id")
                        if not file_id:
                            raise RuntimeError(f"Files API 上传未返回 id: {upload_resp}")
                        url_val = f"file_id://{file_id}"
                        audit_entry["transport"] = "ark-files-api"
                        audit_entry["file_id"] = file_id

                asset_audit.append(audit_entry)

            if not url_val:
                raise ValueError(f"content[{idx}] 缺少 url 或 asset。")

            out_item: dict[str, Any] = {
                "type": item_type,
                item_type: {"url": url_val},
            }
            if role:
                out_item["role"] = role
            resolved_content.append(out_item)
            continue

        resolved_content.append(dict(item))

    merged_prompt = "\n".join(prompt_texts)
    if has_ref_video and ("参考" not in merged_prompt and "reference" not in merged_prompt.lower()):
        warnings.append("提示词中未检测到'参考'关键词，当搭配 reference_video 时建议写明 '参考@video1中的运镜与运动...'。")
    if has_ref_video and ("严格编辑" in merged_prompt or "修改为" in merged_prompt):
        warnings.append("提示词包含编辑关键词，可能触发视频局部编辑模式而非全模态运镜参考。")
    if has_ref_video and not has_ref_image:
        warnings.append("仅输入白模 video_url 而未附带 image_url 参考图，模型材质可能发散或发灰。")

    payload: dict[str, Any] = {
        "model": model,
        "content": resolved_content,
    }
    for key in ("ratio", "duration", "resolution", "generate_audio", "return_last_frame", "draft", "seed", "callback_url"):
        if key in job and job[key] is not None:
            payload[key] = job[key]

    return payload, asset_audit, warnings


def extract_output_urls(history: dict[str, Any]) -> dict[str, str]:
    found: dict[str, str] = {}
    content = history.get("content")
    if isinstance(content, dict):
        if isinstance(content.get("video_url"), str):
            found["video_url"] = content["video_url"]
        if isinstance(content.get("last_frame_url"), str):
            found["last_frame_url"] = content["last_frame_url"]
    elif isinstance(content, list):
        for entry in content:
            if isinstance(entry, dict):
                if isinstance(entry.get("video_url"), dict) and isinstance(entry["video_url"].get("url"), str):
                    found["video_url"] = entry["video_url"]["url"]
                elif isinstance(entry.get("video_url"), str):
                    found["video_url"] = entry["video_url"]
    if isinstance(history.get("video_url"), str) and "video_url" not in found:
        found["video_url"] = history["video_url"]
    return found


def download_file(url: str, target_path: Path, timeout: int = 180) -> Path:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        target_path.write_bytes(resp.read())
    return target_path


def cmd_validate(args: argparse.Namespace) -> int:
    job_path = Path(args.job).resolve()
    job = load_job(job_path)
    payload, audit, warnings = build_payload_and_audit(job, job_path.parent, dry_run=True)
    report = {
        "valid": True,
        "job_file": str(job_path),
        "task_id": job.get("task"),
        "warnings": warnings,
        "assets": audit,
        "dry_run_payload": payload,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def cmd_upload(args: argparse.Namespace) -> int:
    api_key = get_api_key(args.api_key)
    base_url = args.base_url or os.environ.get("ARK_BASE_URL", DEFAULT_BASE_URL)
    file_path = resolve_repo_path(args.file)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    result = upload_file_to_ark(base_url, api_key, file_path, purpose=args.purpose, wait_ready=not args.no_wait)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_submit(args: argparse.Namespace) -> int:
    job_path = Path(args.job).resolve()
    job = load_job(job_path)
    task_dir = resolve_repo_path(job["task_dir"], job_path.parent) if job.get("task_dir") else job_path.parent
    sub_file = task_dir / "submission.json"
    if sub_file.exists() and not args.force and not args.dry_run:
        raise RuntimeError(f"任务目录已有 submission.json（拒绝重复扣费提交）: {sub_file}")

    base_url = args.base_url or os.environ.get("ARK_BASE_URL", DEFAULT_BASE_URL)
    api_key = None if args.dry_run else get_api_key(args.api_key)
    payload, audit, warnings = build_payload_and_audit(
        job,
        job_path.parent,
        dry_run=args.dry_run,
        base_url=base_url,
        api_key=api_key,
        upload_images=args.upload_images,
    )

    if args.dry_run:
        print(json.dumps({"dry_run": True, "warnings": warnings, "assets": audit, "payload": payload}, ensure_ascii=False, indent=2))
        return 0

    endpoint = f"{base_url.rstrip('/')}/contents/generations/tasks"
    resp = http_json_request("POST", endpoint, api_key, payload)
    task_dir.mkdir(parents=True, exist_ok=True)
    sub_record = {
        "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "endpoint": endpoint,
        "response": resp,
    }
    exec_record = {
        "job_file": str(job_path),
        "warnings": warnings,
        "assets": audit,
        "payload_summary": {k: v for k, v in payload.items() if k != "content"},
    }
    sub_file.write_text(json.dumps(sub_record, ensure_ascii=False, indent=2), encoding="utf-8")
    (task_dir / "execution.json").write_text(json.dumps(exec_record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(sub_record, ensure_ascii=False, indent=2))
    return 0


def cmd_collect(args: argparse.Namespace) -> int:
    task_dir = resolve_repo_path(args.task_dir)
    sub_file = task_dir / "submission.json"
    if not sub_file.exists():
        raise FileNotFoundError(f"未找到 submission.json: {sub_file}")

    sub_data = json.loads(sub_file.read_text(encoding="utf-8"))
    remote_id = sub_data.get("response", {}).get("id")
    if not remote_id:
        raise ValueError(f"submission.json 中无有效任务 id: {sub_file}")

    api_key = get_api_key(args.api_key)
    base_url = args.base_url or os.environ.get("ARK_BASE_URL", DEFAULT_BASE_URL)
    poll_url = f"{base_url.rstrip('/')}/contents/generations/tasks/{remote_id}"

    deadline = time.time() + args.timeout
    history: dict[str, Any] = {}
    while True:
        history = http_json_request("GET", poll_url, api_key)
        status = str(history.get("status", "")).lower()
        print(f"[Seedance] task={remote_id} status={status}", flush=True)
        if status in {"succeeded", "failed", "cancelled"}:
            break
        if not args.wait or time.time() >= deadline:
            break
        time.sleep(args.poll_interval)

    (task_dir / "history.json").write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    urls = extract_output_urls(history)
    saved: dict[str, str] = {}
    output_dir = task_dir / "output"
    stem = args.name or task_dir.name

    if "video_url" in urls:
        vid_path = download_file(urls["video_url"], output_dir / f"{stem}_seedance.mp4")
        saved["video"] = str(vid_path)
    if "last_frame_url" in urls:
        img_path = download_file(urls["last_frame_url"], output_dir / f"{stem}_last_frame.png")
        saved["last_frame"] = str(img_path)

    outputs_meta = {
        "remote_id": remote_id,
        "status": history.get("status"),
        "urls": urls,
        "saved_files": saved,
    }
    (task_dir / "outputs.json").write_text(json.dumps(outputs_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(outputs_meta, ensure_ascii=False, indent=2))
    return 0 if str(history.get("status", "")).lower() == "succeeded" else 2


def cmd_run(args: argparse.Namespace) -> int:
    code = cmd_submit(args)
    if args.dry_run or code != 0:
        return code
    job_path = Path(args.job).resolve()
    job = load_job(job_path)
    task_dir = resolve_repo_path(job["task_dir"], job_path.parent) if job.get("task_dir") else job_path.parent
    collect_args = argparse.Namespace(
        task_dir=str(task_dir),
        api_key=args.api_key,
        base_url=args.base_url,
        wait=True,
        poll_interval=args.poll_interval,
        timeout=args.timeout,
        name=job.get("task"),
    )
    return cmd_collect(collect_args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="火山方舟 Doubao Seedance 视频生成 CLI")
    parser.add_argument("--api-key", help="火山方舟 API Key（默认读取环境变量 ARK_API_KEY）")
    parser.add_argument("--base-url", help=f"API 基地址（默认 {DEFAULT_BASE_URL}）")
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", help="本地离线校验任务配置与资产（零消耗）")
    p_val.add_argument("job", help="任务 JSON 配置文件路径")

    p_up = sub.add_parser("upload", help="通过 Files API 上传单个本地媒体文件")
    p_up.add_argument("file", help="本地文件路径")
    p_up.add_argument("--purpose", default="user_data", help="文件用途（默认 user_data）")
    p_up.add_argument("--no-wait", action="store_true", help="上传后不等待服务端处理就绪")

    p_sub = sub.add_parser("submit", help="提交异步生成任务")
    p_sub.add_argument("job", help="任务 JSON 配置文件路径")
    p_sub.add_argument("--dry-run", action="store_true", help="仅预演构造请求体，不实际发网与扣费")
    p_sub.add_argument("--force", action="store_true", help="允许覆盖已存在的 submission.json")
    p_sub.add_argument("--upload-images", action="store_true", help="强制通过 Files API 上传图片（默认 <=4MB 转 Data URI）")

    p_col = sub.add_parser("collect", help="查询任务状态并下载输出")
    p_col.add_argument("task_dir", help="包含 submission.json 的任务目录")
    p_col.add_argument("--wait", action="store_true", help="轮询等待直到任务结束")
    p_col.add_argument("--poll-interval", type=int, default=10, help="轮询间隔秒数（默认 10）")
    p_col.add_argument("--timeout", type=int, default=1800, help="等待超时秒数（默认 1800）")
    p_col.add_argument("--name", help="下载视频文件名前缀")

    p_run = sub.add_parser("run", help="提交任务并自动轮询下载结果")
    p_run.add_argument("job", help="任务 JSON 配置文件路径")
    p_run.add_argument("--dry-run", action="store_true", help="仅预演，不实际提交")
    p_run.add_argument("--force", action="store_true", help="允许覆盖已存在的 submission.json")
    p_run.add_argument("--upload-images", action="store_true", help="强制通过 Files API 上传图片")
    p_run.add_argument("--poll-interval", type=int, default=10, help="轮询间隔秒数（默认 10）")
    p_run.add_argument("--timeout", type=int, default=1800, help="等待超时秒数（默认 1800）")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "validate": cmd_validate,
        "upload": cmd_upload,
        "submit": cmd_submit,
        "collect": cmd_collect,
        "run": cmd_run,
    }
    try:
        return handlers[args.command](args)
    except Exception as exc:
        print(f"[Seedance ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

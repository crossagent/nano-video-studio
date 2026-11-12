"""
platform/seedance/openrouter_client.py
OpenRouter Video Generation API (/api/v1/videos) 通用客户端，
复用 platform/seedance/client.py 中的本地资产校验、SHA-256 审计与 .env 读取逻辑。
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import client as base_client  # noqa: E402

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_openrouter_key(explicit_key: str | None = None) -> str:
    dotenv = base_client.load_repo_dotenv()
    key = (explicit_key or os.environ.get("OPENROUTER_API_KEY") or dotenv.get("OPENROUTER_API_KEY") or "").strip()
    if not key:
        raise RuntimeError(
            "未检测到 OPENROUTER_API_KEY。请在项目根目录 .env 添加 OPENROUTER_API_KEY=...，或使用 --dry-run / validate 验证。"
        )
    return key


def encode_media_data_uri(path: Path, kind: str) -> str:
    if kind == "image_url":
        return base_client.encode_image_data_uri(path)
    ext = path.suffix.lower().lstrip(".") or "mp4"
    mime, _ = mimetypes.guess_type(str(path))
    mime = mime or f"video/{ext}"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def build_openrouter_payload(
    job: dict[str, Any],
    job_dir: Path,
    dry_run: bool = True,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    dotenv = base_client.load_repo_dotenv()
    model = os.environ.get("OPENROUTER_VIDEO_MODEL") or dotenv.get("OPENROUTER_VIDEO_MODEL") or job.get("model") or ""
    if not model:
        raise ValueError("job.json 缺少 'model'（例如 bytedance/seedance-2.5）。")

    prompt = str(job.get("prompt", "")).strip()
    if not prompt:
        raise ValueError("job.json 必须包含非空 'prompt'。")

    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
    }
    for key in ("duration", "resolution", "aspect_ratio", "generate_audio", "seed", "callback_url", "previous_job_id", "provider"):
        if key in job and job[key] is not None:
            payload[key] = job[key]

    asset_audit: list[dict[str, Any]] = []
    warnings: list[str] = []

    def resolve_media_entries(entries: list[dict[str, Any]], field_name: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for idx, entry in enumerate(entries):
            item = dict(entry)
            item_type = item.get("type", "image_url")
            asset_ref = item.pop("asset", None)
            if asset_ref:
                local_path = base_client.resolve_repo_path(asset_ref, job_dir)
                if not local_path.exists():
                    raise FileNotFoundError(f"找不到本地资产文件: {local_path}")
                size_bytes = local_path.stat().st_size
                digest = base_client.sha256_file(local_path)
                rel_asset = (
                    str(local_path.relative_to(base_client.REPO_ROOT)).replace("\\", "/")
                    if local_path.is_relative_to(base_client.REPO_ROOT)
                    else str(local_path)
                )
                asset_audit.append(
                    {
                        "field": field_name,
                        "index": idx,
                        "type": item_type,
                        "asset": rel_asset,
                        "size_bytes": size_bytes,
                        "sha256": digest,
                        "transport": "dry-run" if dry_run else "data-uri-base64",
                    }
                )
                url_val = (
                    f"<dry-run:{local_path.name};bytes={size_bytes};sha256={digest[:12]}>"
                    if dry_run
                    else encode_media_data_uri(local_path, item_type)
                )
                if field_name == "frame_images":
                    item["image_url"] = {"url": url_val}
                elif item_type in {"image_url", "video_url", "audio_url"}:
                    item[item_type] = {"url": url_val}
                else:
                    raise ValueError(f"不支持的引用类型: {item_type}")
            out.append(item)
        return out

    if isinstance(job.get("frame_images"), list) and job["frame_images"]:
        payload["frame_images"] = resolve_media_entries(job["frame_images"], "frame_images")

    if isinstance(job.get("input_references"), list) and job["input_references"]:
        payload["input_references"] = resolve_media_entries(job["input_references"], "input_references")

    has_video = any(a["type"] == "video_url" for a in asset_audit) or any(
        isinstance(r, dict) and r.get("type") == "video_url" for r in payload.get("input_references", [])
    )
    has_image = any(a["type"] == "image_url" for a in asset_audit) or any(
        isinstance(r, dict) and r.get("type") == "image_url" for r in payload.get("input_references", [])
    )
    if has_video and not has_image and not payload.get("frame_images"):
        warnings.append("仅输入白模 video_url 而未附带参考图，模型外观材质可能发散。")
    if "frame_images" in payload and "input_references" in payload:
        warnings.append("OpenRouter 规范提示同时传入 frame_images 与 input_references 时，frame_images 可能影响参考权重。")

    return payload, asset_audit, warnings


def download_with_optional_auth(url: str, target_path: Path, api_key: str | None = None, timeout: int = 180) -> Path:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "nano-video-studio/1.0"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        target_path.write_bytes(resp.read())
    return target_path


def cmd_validate(args: argparse.Namespace) -> int:
    job_path = Path(args.job).resolve()
    job = base_client.load_job(job_path)
    payload, audit, warnings = build_openrouter_payload(job, job_path.parent, dry_run=True)
    print(
        json.dumps(
            {
                "valid": True,
                "provider": "openrouter",
                "job_file": str(job_path),
                "task_id": job.get("task"),
                "warnings": warnings,
                "assets": audit,
                "dry_run_payload": payload,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_submit(args: argparse.Namespace) -> int:
    job_path = Path(args.job).resolve()
    job = base_client.load_job(job_path)
    task_dir = base_client.resolve_repo_path(job["task_dir"], job_path.parent) if job.get("task_dir") else job_path.parent
    sub_file = task_dir / "submission.json"
    if sub_file.exists() and not args.force and not args.dry_run:
        raise RuntimeError(f"任务目录已有 submission.json（拒绝重复扣费提交）: {sub_file}")

    payload, audit, warnings = build_openrouter_payload(job, job_path.parent, dry_run=args.dry_run)
    if args.dry_run:
        print(
            json.dumps(
                {"dry_run": True, "provider": "openrouter", "warnings": warnings, "assets": audit, "payload": payload},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    api_key = get_openrouter_key(args.api_key)
    base_url = (args.base_url or os.environ.get("OPENROUTER_BASE_URL") or OPENROUTER_BASE_URL).rstrip("/")
    endpoint = f"{base_url}/videos"
    resp = base_client.http_json_request("POST", endpoint, api_key, payload, timeout=180)

    task_dir.mkdir(parents=True, exist_ok=True)
    sub_record = {
        "provider": "openrouter",
        "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "endpoint": endpoint,
        "response": resp,
    }
    exec_record = {
        "job_file": str(job_path),
        "warnings": warnings,
        "assets": audit,
        "payload_summary": {k: v for k, v in payload.items() if k not in {"input_references", "frame_images"}},
    }
    sub_file.write_text(json.dumps(sub_record, ensure_ascii=False, indent=2), encoding="utf-8")
    (task_dir / "execution.json").write_text(json.dumps(exec_record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(sub_record, ensure_ascii=False, indent=2))
    return 0


def cmd_collect(args: argparse.Namespace) -> int:
    task_dir = base_client.resolve_repo_path(args.task_dir)
    sub_file = task_dir / "submission.json"
    if not sub_file.exists():
        raise FileNotFoundError(f"未找到 submission.json: {sub_file}")

    sub_data = json.loads(sub_file.read_text(encoding="utf-8"))
    job_id = sub_data.get("response", {}).get("id")
    if not job_id:
        raise ValueError(f"submission.json 中无有效 job id: {sub_file}")

    api_key = get_openrouter_key(args.api_key)
    base_url = (args.base_url or os.environ.get("OPENROUTER_BASE_URL") or OPENROUTER_BASE_URL).rstrip("/")
    poll_url = f"{base_url}/videos/{job_id}"

    deadline = time.time() + args.timeout
    history: dict[str, Any] = {}
    while True:
        history = base_client.http_json_request("GET", poll_url, api_key)
        status = str(history.get("status", "")).lower()
        print(f"[OpenRouter] job={job_id} status={status}", flush=True)
        if status in {"completed", "failed", "cancelled", "expired"}:
            break
        if not args.wait or time.time() >= deadline:
            break
        time.sleep(args.poll_interval)

    (task_dir / "history.json").write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

    saved: dict[str, str] = {}
    output_dir = task_dir / "output"
    stem = args.name or task_dir.name
    if str(history.get("status", "")).lower() == "completed":
        out_path = output_dir / f"{stem}_openrouter.mp4"
        signed_urls = history.get("urls") or []
        unsigned_urls = history.get("unsigned_urls") or []
        if signed_urls:
            download_with_optional_auth(signed_urls[0], out_path)
        elif unsigned_urls:
            download_with_optional_auth(unsigned_urls[0], out_path, api_key=api_key)
        else:
            download_with_optional_auth(f"{base_url}/videos/{job_id}/content?index=0", out_path, api_key=api_key)
        saved["video"] = str(out_path)

    outputs_meta = {
        "provider": "openrouter",
        "job_id": job_id,
        "status": history.get("status"),
        "usage": history.get("usage"),
        "urls": history.get("urls"),
        "unsigned_urls": history.get("unsigned_urls"),
        "saved_files": saved,
    }
    (task_dir / "outputs.json").write_text(json.dumps(outputs_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(outputs_meta, ensure_ascii=False, indent=2))
    return 0 if str(history.get("status", "")).lower() == "completed" else 2


def cmd_run(args: argparse.Namespace) -> int:
    code = cmd_submit(args)
    if args.dry_run or code != 0:
        return code
    job_path = Path(args.job).resolve()
    job = base_client.load_job(job_path)
    task_dir = base_client.resolve_repo_path(job["task_dir"], job_path.parent) if job.get("task_dir") else job_path.parent
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
    parser = argparse.ArgumentParser(description="OpenRouter Video Generation (/api/v1/videos) CLI")
    parser.add_argument("--api-key", help="OpenRouter API Key（默认读取 .env 中的 OPENROUTER_API_KEY）")
    parser.add_argument("--base-url", help=f"API 基地址（默认 {OPENROUTER_BASE_URL}）")
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", help="本地离线校验任务配置（零消耗）")
    p_val.add_argument("job")

    p_sub = sub.add_parser("submit", help="提交异步视频生成任务")
    p_sub.add_argument("job")
    p_sub.add_argument("--dry-run", action="store_true")
    p_sub.add_argument("--force", action="store_true")

    p_col = sub.add_parser("collect", help="查询任务状态并下载视频")
    p_col.add_argument("task_dir")
    p_col.add_argument("--wait", action="store_true")
    p_col.add_argument("--poll-interval", type=int, default=10)
    p_col.add_argument("--timeout", type=int, default=1800)
    p_col.add_argument("--name")

    p_run = sub.add_parser("run", help="提交并轮询下载结果")
    p_run.add_argument("job")
    p_run.add_argument("--dry-run", action="store_true")
    p_run.add_argument("--force", action="store_true")
    p_run.add_argument("--poll-interval", type=int, default=10)
    p_run.add_argument("--timeout", type=int, default=1800)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "validate": cmd_validate,
        "submit": cmd_submit,
        "collect": cmd_collect,
        "run": cmd_run,
    }
    try:
        return handlers[args.command](args)
    except Exception as exc:
        print(f"[OpenRouter ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

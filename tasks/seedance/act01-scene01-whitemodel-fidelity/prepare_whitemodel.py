"""
tasks/seedance/act01-scene01-whitemodel-fidelity/prepare_whitemodel.py
从最新候选工程 act01_scene01_roadside_strike.blend 无损生成：
1. 纯中性灰度 Clay 白模工程（消除高饱和色彩渗漏，强化 Cavity + Shadow 光流梯度）
2. 几何体与屏幕占比体检报告 (probe_report.json)
3. 分镜独立段与连贯段的中性白模 MP4 视频与首帧 PNG
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


REPO_ROOT = Path(__file__).resolve().parents[3]
TASK_DIR = Path(__file__).resolve().parent
WORK_DIR = TASK_DIR / "work"
INPUTS_DIR = TASK_DIR / "inputs"

# 中性纯灰阶映射表 (R=G=B, Saturation=0.0)，确保零色偏渗漏且层间对比度清晰
NEUTRAL_GRAY_MAP = {
    "S01_Basalt": (0.34, 0.34, 0.34, 1.0),
    "S01_Talus": (0.48, 0.48, 0.48, 1.0),
    "S01_Valley_Floor": (0.58, 0.58, 0.58, 1.0),
    "S01_Wheat_Beds": (0.70, 0.70, 0.70, 1.0),
    "S01_Road_Mud": (0.46, 0.46, 0.46, 1.0),
    "S01_Wheel_Ruts": (0.32, 0.32, 0.32, 1.0),
    "S01_Drainage": (0.40, 0.40, 0.40, 1.0),
    "S01_Roadside_Basalt": (0.56, 0.56, 0.56, 1.0),
    "S01_New_Fracture": (0.80, 0.80, 0.80, 1.0),
    "S01_Tread_Link_Metal": (0.48, 0.48, 0.48, 1.0),
    "S01_Road_Strike_Core": (1.00, 1.00, 1.00, 1.0),
    "S01_Road_Strike_Fork": (0.96, 0.96, 0.96, 1.0),
    "Mat_HarvesterRed": (0.85, 0.85, 0.85, 1.0),
    "Mat_SteelPolished": (0.88, 0.88, 0.88, 1.0),
    "Mat_MetalRust": (0.72, 0.72, 0.72, 1.0),
    "Mat_ConsoleCasing": (0.50, 0.50, 0.50, 1.0),
    "Mat_GlassCyan": (0.54, 0.54, 0.54, 0.75),
    "Mat_Treads": (0.28, 0.28, 0.28, 1.0),
    "Mat_StatusYellow": (0.94, 0.94, 0.94, 1.0),
    "Mat_WhiteLamp": (0.98, 0.98, 0.98, 1.0),
    "Mat_AlertRed": (0.82, 0.82, 0.82, 1.0),
    "Mat_HumanSuitBlue": (0.44, 0.44, 0.44, 1.0),
    "Mat_HumanSuitOrange": (0.52, 0.52, 0.52, 1.0),
    "Mat_Skin": (0.64, 0.64, 0.64, 1.0),
}

SHOTS = [
    {
        "id": "s01_010",
        "label": "S01-010 峡谷俯冲进场",
        "camera": "CAM_S01-010",
        "start": 1,
        "end": 144,
        "subject": None,
    },
    {
        "id": "s01_020",
        "label": "S01-020 山脚落雷碎石",
        "camera": "CAM_S01-020",
        "start": 145,
        "end": 228,
        "subject": "FX_Roadside_Intact_Rock",
    },
    {
        "id": "s01_030",
        "label": "S01-030 右履带碾过碎石",
        "camera": "CAM_S01-030",
        "start": 229,
        "end": 300,
        "subject": "Harvester_Root",
    },
    {
        "id": "s01_040",
        "label": "S01-040 收割机侧后跟拍（主基准）",
        "camera": "CAM_S01-040",
        "start": 301,
        "end": 432,
        "subject": "Harvester_Root",
    },
]

CLIPS = [
    *SHOTS,
    {
        "id": "s01_020_040",
        "label": "S01-020–040 落雷碾压连续动作段 (8.5s)",
        "camera": None,  # 沿用时间轴 Marker 自动切镜
        "start": 145,
        "end": 348,
        "subject": None,
    },
]


def neutral_gray_value(rgba):
    # 若存在未在显式表中的材质，按感知亮度去饱和为中性灰
    lum = 0.2126 * rgba[0] + 0.7152 * rgba[1] + 0.0722 * rgba[2]
    lum = max(0.28, min(0.92, lum * 0.7 + 0.22))
    alpha = rgba[3] if len(rgba) > 3 else 1.0
    return (lum, lum, lum, alpha)


def apply_neutral_clay_setup(scene: bpy.types.Scene) -> None:
    scene.render.engine = "BLENDER_WORKBENCH"
    shading = scene.display.shading
    shading.light = "STUDIO"
    shading.studio_light = "Default"
    shading.color_type = "MATERIAL"
    shading.show_cavity = True
    shading.cavity_type = "BOTH"
    shading.cavity_ridge_factor = 1.8
    shading.cavity_valley_factor = 1.5
    shading.show_shadows = True
    shading.shadow_intensity = 0.55
    shading.show_object_outline = False

    scene.display.shading.background_type = "WORLD"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("Neutral_Clay_World")
    scene.world.color = (0.74, 0.74, 0.74)

    # 统一标准色彩管理，防止暗部发死与闪电过曝锁死
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    if scene.animation_data and scene.animation_data.action:
        # 温和化闪电过曝峰值（Blender 5.x slotted action API）
        scene.animation_data.action = scene.animation_data.action.copy()
        anim = scene.animation_data
        for layer in anim.action.layers:
            for strip in layer.strips:
                channel = strip.channelbag(anim.action_slot)
                for fcurve in channel.fcurves:
                    if fcurve.data_path == "view_settings.exposure":
                        for kp in fcurve.keyframe_points:
                            kp.co.y = min(kp.co.y, 0.35)
                            kp.handle_left.y = min(kp.handle_left.y, 0.35)
                            kp.handle_right.y = min(kp.handle_right.y, 0.35)

    for mat in bpy.data.materials:
        target = NEUTRAL_GRAY_MAP.get(mat.name) or neutral_gray_value(mat.diffuse_color)
        mat.diffuse_color = target
        mat.roughness = 0.65
        mat.metallic = 0.0
        if mat.use_nodes and mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    node.inputs["Base Color"].default_value = target
                    node.inputs["Roughness"].default_value = 0.65
                    node.inputs["Metallic"].default_value = 0.0

    # 统一 1280x536 (精确维持 2.39:1 宽银幕比例且宽高均被 8 整除，适配主流视频模型编码)
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 536
    scene.render.resolution_percentage = 100
    scene.render.fps = 24
    scene.render.fps_base = 1.0


def mesh_world_corners(root_obj: bpy.types.Object) -> list[Vector]:
    objs = [root_obj] + list(root_obj.children_recursive)
    pts: list[Vector] = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in objs:
        if obj.type != "MESH" or obj.hide_render:
            continue
        eval_obj = obj.evaluated_get(depsgraph)
        for corner in eval_obj.bound_box:
            pts.append(eval_obj.matrix_world @ Vector(corner))
    return pts


def probe_shot(scene: bpy.types.Scene, shot: dict) -> dict:
    cam = bpy.data.objects[shot["camera"]]
    sample_frames = sorted({shot["start"], (shot["start"] + shot["end"]) // 2, shot["end"]})
    if shot["id"] == "s01_020":
        sample_frames = [145, 178, 179, 200, 228]

    frame_stats = []
    for frame in sample_frames:
        scene.frame_set(frame)
        entry = {"frame": frame, "camera_location": [round(v, 3) for v in cam.matrix_world.translation]}
        if shot["subject"] and shot["subject"] in bpy.data.objects:
            subj = bpy.data.objects[shot["subject"]]
            pts = mesh_world_corners(subj)
            if pts:
                coords = [world_to_camera_view(scene, cam, p) for p in pts]
                in_front = [c for c in coords if c.z > 0]
                if in_front:
                    xs = [max(0.0, min(1.0, c.x)) for c in in_front]
                    ys = [max(0.0, min(1.0, c.y)) for c in in_front]
                    w = max(xs) - min(xs)
                    h = max(ys) - min(ys)
                    entry["subject_coverage"] = {
                        "width_pct": round(w * 100, 1),
                        "height_pct": round(h * 100, 1),
                        "bbox_area_pct": round(w * h * 100, 1),
                        "clipped": any(c.x < 0 or c.x > 1 or c.y < 0 or c.y > 1 for c in in_front),
                    }
        frame_stats.append(entry)

    # 评估主体最小可见比例是否达标（经验门槛：核心刚体面积或宽度占比 >= 15%）
    coverages = [f["subject_coverage"]["width_pct"] for f in frame_stats if "subject_coverage" in f]
    passed = True
    notes = []
    if coverages:
        min_w = min(coverages)
        if min_w < 15.0:
            passed = False
            notes.append(f"部分帧主体宽度占比仅 {min_w}% (<15%)，视频模型存在跟踪丢失风险。")
        else:
            notes.append(f"主体最小屏幕宽度占比 {min_w}%，满足稠密光流追踪门槛。")
    else:
        notes.append("纯相机大场景俯冲调度镜头，依靠地形脊线与麦垄线条提供连续光流梯度。")

    return {
        "shot_id": shot["id"],
        "label": shot["label"],
        "frames": [shot["start"], shot["end"]],
        "duration_sec": round((shot["end"] - shot["start"] + 1) / 24.0, 2),
        "probe_passed": passed,
        "notes": notes,
        "samples": frame_stats,
    }


def render_frames_and_encode(scene: bpy.types.Scene, clip: dict) -> dict:
    # 1. 先单独导出首帧 PNG，便于视觉检查与参考图透视对照
    first_frame_dst = INPUTS_DIR / f"{clip['id']}_first_frame_clay.png"
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 15
    scene.frame_set(clip["start"])
    if clip["camera"]:
        scene.camera = bpy.data.objects[clip["camera"]]
    else:
        best_frame = -1
        for marker in scene.timeline_markers:
            if marker.camera and marker.frame <= clip["start"] and marker.frame >= best_frame:
                best_frame = marker.frame
                scene.camera = marker.camera
    scene.render.filepath = str(first_frame_dst)
    bpy.ops.render.render(write_still=True)

    # 2. 使用 Blender 5.2 内置 FFmpeg H.264 编码器直接渲染白模 MP4（timeline_markers 自动切镜）
    mp4_path = INPUTS_DIR / f"{clip['id']}_clay.mp4"
    scene.render.image_settings.media_type = "VIDEO"
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    scene.render.ffmpeg.audio_codec = "NONE"

    scene.frame_start = clip["start"]
    scene.frame_end = clip["end"]
    if clip["camera"]:
        scene.camera = bpy.data.objects[clip["camera"]]
    scene.render.filepath = str(mp4_path)
    bpy.ops.render.render(animation=True)

    return {
        "clip_id": clip["id"],
        "label": clip["label"],
        "mp4": str(mp4_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "first_frame_png": str(first_frame_dst.relative_to(REPO_ROOT)).replace("\\", "/"),
        "frames": clip["end"] - clip["start"] + 1,
        "duration_sec": round((clip["end"] - clip["start"] + 1) / 24.0, 2),
        "size_bytes": mp4_path.stat().st_size,
    }


def main() -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    (TASK_DIR / "output").mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    apply_neutral_clay_setup(scene)

    clay_blend = WORK_DIR / "act01_scene01_neutral_clay.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(clay_blend))
    print(f"[Prep] Saved neutral clay blend: {clay_blend}", flush=True)

    probes = [probe_shot(scene, shot) for shot in SHOTS]
    rendered = []
    render_targets = CLIPS
    if "--only" in sys.argv:
        idx = sys.argv.index("--only")
        wanted = set(sys.argv[idx + 1].split(","))
        render_targets = [c for c in CLIPS if c["id"] in wanted]

    for clip in render_targets:
        print(f"[Prep] Rendering {clip['id']} ({clip['start']}..{clip['end']})...", flush=True)
        rendered.append(render_frames_and_encode(scene, clip))

    report = {
        "source_blend": "tasks/blender/act01-scene01-previs/work/act01_scene01_roadside_strike.blend",
        "neutral_clay_blend": "tasks/seedance/act01-scene01-whitemodel-fidelity/work/act01_scene01_neutral_clay.blend",
        "resolution": "1280x536",
        "fps": 24,
        "probes": probes,
        "rendered_clips": rendered,
    }
    report_path = TASK_DIR / "probe_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Prep] Done! Report saved to {report_path}", flush=True)


if __name__ == "__main__":
    main()

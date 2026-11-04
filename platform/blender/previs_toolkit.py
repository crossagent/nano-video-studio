"""
platform/blender/previs_toolkit.py
影视级 3D Previs 与相机调度通用工具库 (Universal Previs Toolkit for Blender 5.x)
供 tasks/blender/<task-id>/ 脚本调用，统一构图、材质、相机矩阵与快照输出规范。
"""

import bpy
import math
import os

def init_previs_scene(clear_defaults=True, width=1920, height=804, fps=24, engine='BLENDER_WORKBENCH'):
    """
    初始化 Previs 场景，默认配置 2.39:1 变形宽银幕（1920x804）与高对比度视口。
    """
    if clear_defaults:
        bpy.ops.wm.read_factory_settings(use_empty=True)
    
    scene = bpy.context.scene
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    
    scene.render.engine = engine
    if engine == 'BLENDER_WORKBENCH':
        shading = scene.display.shading
        shading.light = 'STUDIO'
        shading.color_type = 'MATERIAL'
        shading.show_cavity = True
        shading.cavity_type = 'BOTH'
        shading.cavity_ridge_factor = 2.0
        shading.cavity_valley_factor = 1.5
        shading.show_shadows = True
    return scene

def create_previs_material(name, diffuse_color, roughness=0.5, metallic=0.0, emission_color=(0,0,0,1), emission_strength=0.0):
    """
    创建标准 Previs 着色材质（支持 Workbench 视口色彩与 Cycles/EEVEE 节点渲染）。
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = diffuse_color
    node_bsdf.inputs['Roughness'].default_value = roughness
    node_bsdf.inputs['Metallic'].default_value = metallic
    if 'Emission Color' in node_bsdf.inputs:
        node_bsdf.inputs['Emission Color'].default_value = emission_color
        node_bsdf.inputs['Emission Strength'].default_value = emission_strength
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    
    # Workbench 视口显示参数
    mat.diffuse_color = diffuse_color
    mat.roughness = roughness
    mat.metallic = metallic
    return mat

def create_previs_camera(name, location, rotation_deg, focal_length=35.0, clip_end=2000.0, collection=None):
    """
    按指定欧拉角（度数）和毫米焦距构建摄影机。
    """
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = focal_length
    cam_data.clip_end = clip_end
    cam_data.display_size = 1.5
    
    cam_obj = bpy.data.objects.new(name, cam_data)
    cam_obj.location = location
    cam_obj.rotation_euler = (
        math.radians(rotation_deg[0]),
        math.radians(rotation_deg[1]),
        math.radians(rotation_deg[2])
    )
    
    target_col = collection if collection else bpy.context.scene.collection
    target_col.objects.link(cam_obj)
    return cam_obj

def render_camera_snapshots(cameras_dict, output_dir):
    """
    批量渲染摄像机视口快照，保存为 PNG 静帧。
    """
    os.makedirs(output_dir, exist_ok=True)
    scene = bpy.context.scene
    saved_renders = []
    
    for cam_name, cam_obj in cameras_dict.items():
        scene.camera = cam_obj
        filepath = os.path.join(output_dir, f"{cam_name}.png")
        scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)
        saved_renders.append(filepath)
        print(f"[Platform/Blender] Rendered snapshot: {filepath}")
        
    return saved_renders

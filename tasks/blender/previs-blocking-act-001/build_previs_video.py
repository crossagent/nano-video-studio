"""
tasks/blender/previs-blocking-act-001/build_previs_video.py
《星际争霸：萨尔那加之影》第一幕 3D 白模分镜动画预演（Previs 2.0 升级版）
核心改进：
1. 【具象化人体假人与道具】增加带头、躯干、四肢的人形模特（拉尔斯、奥克塔维亚、刀锋女王凯瑞甘剪影），彻底告别抽象方块；
2. 【丰富场景关键道具】板房晃动吊灯、地震仪刻度滚筒、裂谷边缘微缩收割机比例尺、神庙发光浮雕导轨与结晶门；
3. 【具象化粒子瓦解与通天信标】拉尔斯悬浮升空、发光粒子群消散、400米宇宙信标贯穿云层；
4. 【电影级导演监视器字幕条 (HUD Overlay)】逐帧合成高对比度镜头编号、机位焦段、剧情动作、视听意图与台词提示。
"""

import bpy
import math
import os
import glob
import sys
import site

# 引入用户环境 site-packages (包含 cv2 和 PIL)
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.append(user_site)

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def setup_video_scene(frames_dir):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    
    # 2.39:1 变形宽银幕电影规格 (1920 x 804)
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 804
    scene.render.resolution_percentage = 100
    scene.render.fps = 24
    
    scene.frame_start = 1
    scene.frame_end = 792
    
    # 渲染引擎：Workbench 高对比度白模预演模式
    scene.render.engine = 'BLENDER_WORKBENCH'
    shading = scene.display.shading
    shading.light = 'STUDIO'
    shading.color_type = 'MATERIAL'
    shading.show_cavity = True
    shading.cavity_type = 'BOTH'
    shading.cavity_ridge_factor = 2.0
    shading.cavity_valley_factor = 1.5
    shading.show_shadows = True
    
    os.makedirs(frames_dir, exist_ok=True)
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(frames_dir, "frame_")
    
    return scene

def create_mat(name, color, roughness=0.5, metallic=0.0, emission_color=(0,0,0,1), emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = color
    node_bsdf.inputs['Roughness'].default_value = roughness
    node_bsdf.inputs['Metallic'].default_value = metallic
    if 'Emission Color' in node_bsdf.inputs:
        node_bsdf.inputs['Emission Color'].default_value = emission_color
        node_bsdf.inputs['Emission Strength'].default_value = emission_strength
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    
    mat.diffuse_color = color
    mat.roughness = roughness
    mat.metallic = metallic
    return mat

def build_materials():
    mats = {}
    mats['Wheat'] = create_mat('Mat_Wheat', (0.75, 0.60, 0.30, 1.0), roughness=0.9)
    mats['Mud'] = create_mat('Mat_Mud', (0.24, 0.18, 0.13, 1.0), roughness=0.95)
    mats['RockDark'] = create_mat('Mat_RockDark', (0.20, 0.19, 0.19, 1.0), roughness=0.85)
    mats['HarvesterRed'] = create_mat('Mat_HarvesterRed', (0.78, 0.14, 0.16, 1.0), roughness=0.4, metallic=0.3)
    mats['Treads'] = create_mat('Mat_Treads', (0.12, 0.12, 0.14, 1.0), roughness=0.7, metallic=0.8)
    mats['GlassCyan'] = create_mat('Mat_GlassCyan', (0.35, 0.85, 0.95, 0.8), roughness=0.1, metallic=0.1)
    mats['MetalRust'] = create_mat('Mat_MetalRust', (0.45, 0.28, 0.18, 1.0), roughness=0.7, metallic=0.5)
    mats['TurretOlive'] = create_mat('Mat_TurretOlive', (0.30, 0.36, 0.22, 1.0), roughness=0.6, metallic=0.5)
    mats['XelNagaObsidian'] = create_mat('Mat_XelNagaObsidian', (0.05, 0.06, 0.08, 1.0), roughness=0.2, metallic=0.9)
    mats['XelNagaGlowBlue'] = create_mat('Mat_XelNagaGlowBlue', (0.1, 0.82, 1.0, 1.0), emission_color=(0.1, 0.82, 1.0, 1.0), emission_strength=8.0)
    mats['BeaconBeam'] = create_mat('Mat_BeaconBeam', (0.9, 0.98, 1.0, 1.0), emission_color=(0.9, 0.98, 1.0, 1.0), emission_strength=18.0)
    mats['CharBasalt'] = create_mat('Mat_CharBasalt', (0.08, 0.07, 0.09, 1.0), roughness=0.9)
    mats['CharLava'] = create_mat('Mat_CharLava', (1.0, 0.28, 0.01, 1.0), emission_color=(1.0, 0.28, 0.01, 1.0), emission_strength=10.0)
    mats['ZergPurple'] = create_mat('Mat_ZergPurple', (0.35, 0.12, 0.42, 1.0), roughness=0.3)
    mats['ZergBone'] = create_mat('Mat_ZergBone', (0.65, 0.60, 0.48, 1.0), roughness=0.4)
    mats['HumanSuitOrange'] = create_mat('Mat_HumanSuitOrange', (0.80, 0.42, 0.15, 1.0), roughness=0.5)
    mats['HumanSuitBlue'] = create_mat('Mat_HumanSuitBlue', (0.22, 0.38, 0.58, 1.0), roughness=0.5)
    mats['Skin'] = create_mat('Mat_Skin', (0.88, 0.72, 0.62, 1.0), roughness=0.6)
    mats['AlertRed'] = create_mat('Mat_AlertRed', (1.0, 0.05, 0.05, 1.0), emission_color=(1.0, 0.05, 0.05, 1.0), emission_strength=12.0)
    mats['WhiteLamp'] = create_mat('Mat_WhiteLamp', (1.0, 1.0, 0.95, 1.0), emission_color=(1.0, 1.0, 0.95, 1.0), emission_strength=10.0)
    return mats

def create_human_dummy(name, loc, rot_deg=(0,0,0), scale=1.0, suit_mat=None, skin_mat=None, parent=None, col=None):
    """
    创建结构清晰、辨识度极高的人形模特（假人）：头盔/头部、躯干胸甲、四肢、腰带
    """
    scene = bpy.context.scene
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
    root.scale = (scale, scale, scale)
    if parent:
        root.parent = parent
    
    if col:
        col.objects.link(root)
    else:
        scene.collection.objects.link(root)
        
    parts = []
    
    # 躯干胸腔 (0.4m x 0.25m x 0.55m)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.25))
    torso = bpy.context.active_object
    torso.scale = (0.42, 0.26, 0.52)
    torso.parent = root
    if suit_mat: torso.data.materials.append(suit_mat)
    parts.append(torso)
    
    # 头部/安全帽 (Sphere 0.18m)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0, 0, 1.72))
    head = bpy.context.active_object
    head.parent = root
    if skin_mat: head.data.materials.append(skin_mat)
    parts.append(head)
    
    # 面罩/面部指示条
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.14, 1.73))
    visor = bpy.context.active_object
    visor.scale = (0.24, 0.06, 0.10)
    visor.parent = root
    if suit_mat: visor.data.materials.append(suit_mat)
    parts.append(visor)
    
    # 手臂与双腿
    for side, sx in [('L', -0.30), ('R', 0.30)]:
        # 上肢手臂
        bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.60, location=(sx, 0, 1.15))
        arm = bpy.context.active_object
        arm.parent = root
        if suit_mat: arm.data.materials.append(suit_mat)
        parts.append(arm)
        
        # 下肢腿部
        bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.85, location=(sx * 0.55, 0, 0.45))
        leg = bpy.context.active_object
        leg.parent = root
        if suit_mat: leg.data.materials.append(suit_mat)
        parts.append(leg)
        
    for p in parts:
        if col:
            col.objects.link(p)
            scene.collection.objects.unlink(p)
            
    return root

def build_sets_and_animations(mats):
    scene = bpy.context.scene
    
    # =========================================================================
    # SET A: 贝卡·罗麦田平原与联合收割机 (X: 0) -> Shot 01, Shot 02, Shot 03
    # =========================================================================
    col_a = bpy.data.collections.new("Set_A_BhekarRo_Plains")
    scene.collection.children.link(col_a)
    
    # 广袤麦田与风暴山脊
    bpy.ops.mesh.primitive_plane_add(size=160, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Plains_Ground_Wheat"
    ground.data.materials.append(mats['Wheat'])
    col_a.objects.link(ground)
    scene.collection.objects.unlink(ground)
    
    for i in range(-6, 7):
        x = i * 14
        y = -65 - abs(i)*3
        h = 28 + (abs(i)*4 % 12) * 3
        w = 15 + (abs(i) % 3) * 2
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h/2))
        mnt = bpy.context.active_object
        mnt.scale = (w, 18, h)
        mnt.name = f"Mountain_{i}"
        mnt.data.materials.append(mats['RockDark'])
        col_a.objects.link(mnt)
        scene.collection.objects.unlink(mnt)
        
    # 联合收割机根节点
    bpy.ops.object.empty_add(type='ARROWS', location=(0, 35, 0))
    harvester_root = bpy.context.active_object
    harvester_root.name = "Harvester_Root"
    col_a.objects.link(harvester_root)
    scene.collection.objects.unlink(harvester_root)
    
    # 车体底盘
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.8))
    chassis = bpy.context.active_object
    chassis.scale = (4.4, 8.4, 2.2)
    chassis.parent = harvester_root
    chassis.name = "Harvester_Chassis"
    chassis.data.materials.append(mats['HarvesterRed'])
    col_a.objects.link(chassis)
    scene.collection.objects.unlink(chassis)
    
    # 粗犷双履带
    for side, x_off in [("L", -2.8), ("R", 2.8)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_off, 0, 1.2))
        tr = bpy.context.active_object
        tr.scale = (1.2, 9.0, 1.8)
        tr.parent = harvester_root
        tr.name = f"Harvester_Track_{side}"
        tr.data.materials.append(mats['Treads'])
        col_a.objects.link(tr)
        scene.collection.objects.unlink(tr)
        
    # 驾驶舱与全景防暴前挡玻璃
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 1.5, 3.5))
    cab = bpy.context.active_object
    cab.scale = (3.4, 3.4, 1.9)
    cab.parent = harvester_root
    cab.data.materials.append(mats['HarvesterRed'])
    col_a.objects.link(cab)
    scene.collection.objects.unlink(cab)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 3.22, 3.6))
    glass = bpy.context.active_object
    glass.scale = (3.0, 0.1, 1.3)
    glass.parent = harvester_root
    glass.data.materials.append(mats['GlassCyan'])
    col_a.objects.link(glass)
    scene.collection.objects.unlink(glass)
    
    # 旋转收割滚筒
    bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=4.8, location=(0, 4.8, 1.2))
    reel = bpy.context.active_object
    reel.rotation_euler = (0, math.radians(90), 0)
    reel.parent = harvester_root
    reel.name = "Harvester_Reel"
    reel.data.materials.append(mats['MetalRust'])
    col_a.objects.link(reel)
    scene.collection.objects.unlink(reel)
    
    # 车顶高亮探照灯
    for lx in [-1.2, 1.2]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.3, location=(lx, 3.2, 4.6))
        light = bpy.context.active_object
        light.rotation_euler = (math.radians(90), 0, 0)
        light.parent = harvester_root
        light.data.materials.append(mats['WhiteLamp'])
        col_a.objects.link(light)
        scene.collection.objects.unlink(light)
    
    # 驾驶舱内坐姿人形假人：拉尔斯 (左驾) 与 奥克塔维亚 (右副驾)
    lars_driver = create_human_dummy("Lars_Driver", (-0.8, 1.5, 2.5), rot_deg=(0,0,0), scale=0.85, 
                                     suit_mat=mats['HumanSuitOrange'], skin_mat=mats['Skin'], parent=harvester_root, col=col_a)
    octavia_copilot = create_human_dummy("Octavia_Copilot", (0.8, 1.5, 2.5), rot_deg=(0,0,0), scale=0.80, 
                                         suit_mat=mats['HumanSuitBlue'], skin_mat=mats['Skin'], parent=harvester_root, col=col_a)
    
    # 收割机疾驰位移动画 (Frame 73 to 144)
    harvester_root.location = (0, 38, 0)
    harvester_root.keyframe_insert(data_path="location", frame=73)
    harvester_root.location = (0, -18, 0)
    harvester_root.keyframe_insert(data_path="location", frame=144)
    
    reel.rotation_euler = (0, math.radians(90), 0)
    reel.keyframe_insert(data_path="rotation_euler", frame=73)
    reel.rotation_euler = (math.radians(1800), math.radians(90), 0)
    reel.keyframe_insert(data_path="rotation_euler", frame=144)

    # =========================================================================
    # SET B: 自由避难所防风圈与旧导弹塔 (X: 250) -> Shot 04
    # =========================================================================
    col_b = bpy.data.collections.new("Set_B_FreeHaven_Perimeter")
    scene.collection.children.link(col_b)
    bx = 250
    
    bpy.ops.mesh.primitive_plane_add(size=120, location=(bx, 0, 0))
    fh_ground = bpy.context.active_object
    fh_ground.data.materials.append(mats['Mud'])
    col_b.objects.link(fh_ground)
    scene.collection.objects.unlink(fh_ground)
    
    # 八角形防风阻隔堤坝
    for i in range(8):
        ang = i * (2 * math.pi / 8)
        px = bx + math.cos(ang) * 38
        py = math.sin(ang) * 38
        bpy.ops.mesh.primitive_cube_add(size=1, location=(px, py, 1.8))
        wall = bpy.context.active_object
        wall.scale = (24, 4, 3.6)
        wall.rotation_euler = (0, 0, ang + math.pi/2)
        wall.data.materials.append(mats['RockDark'])
        col_b.objects.link(wall)
        scene.collection.objects.unlink(wall)
        
    # 双联装老式防空导弹塔
    tx, ty = bx - 6, 16
    bpy.ops.mesh.primitive_cylinder_add(radius=2.0, depth=6.5, location=(tx, ty, 3.25))
    pylon = bpy.context.active_object
    pylon.data.materials.append(mats['MetalRust'])
    col_b.objects.link(pylon)
    scene.collection.objects.unlink(pylon)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(tx, ty, 7.2))
    thead = bpy.context.active_object
    thead.scale = (3.6, 2.8, 1.6)
    thead.data.materials.append(mats['TurretOlive'])
    col_b.objects.link(thead)
    scene.collection.objects.unlink(thead)
    
    for side, off in [("L", -2.4), ("R", 2.4)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(tx + off, ty, 7.6))
        pod = bpy.context.active_object
        pod.scale = (1.5, 3.4, 1.8)
        pod.rotation_euler = (math.radians(-18), 0, 0)
        pod.data.materials.append(mats['TurretOlive'])
        col_b.objects.link(pod)
        scene.collection.objects.unlink(pod)
        
    bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=0.25, location=(tx, ty, 9.0))
    dish = bpy.context.active_object
    dish.rotation_euler = (math.radians(45), 0, 0)
    dish.data.materials.append(mats['MetalRust'])
    col_b.objects.link(dish)
    scene.collection.objects.unlink(dish)
    
    dish.rotation_euler = (math.radians(45), 0, 0)
    dish.keyframe_insert(data_path="rotation_euler", frame=217)
    dish.rotation_euler = (math.radians(45), 0, math.radians(720))
    dish.keyframe_insert(data_path="rotation_euler", frame=288)

    # =========================================================================
    # SET C: 兄妹活动预制板房内景 (X: 500) -> Shot 05, Shot 06, Shot 07
    # =========================================================================
    col_c = bpy.data.collections.new("Set_C_Homestead_Interior")
    scene.collection.children.link(col_c)
    cx = 500
    
    # 房间外壳框架与四壁
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, 0, 2.2))
    room = bpy.context.active_object
    room.scale = (9.0, 7.0, 4.4)
    room.data.materials.append(mats['RockDark'])
    col_c.objects.link(room)
    scene.collection.objects.unlink(room)
    
    # 工作台与控制台面板
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx + 2.5, 0, 1.0))
    bench = bpy.context.active_object
    bench.scale = (1.8, 4.5, 1.2)
    bench.data.materials.append(mats['MetalRust'])
    col_c.objects.link(bench)
    scene.collection.objects.unlink(bench)
    
    # 地震仪基座与图纸记录滚筒 (清楚表明这是地震记录仪)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx + 2.4, -0.4, 1.8))
    seismo_base = bpy.context.active_object
    seismo_base.scale = (0.9, 1.2, 0.5)
    seismo_base.data.materials.append(mats['TurretOlive'])
    col_c.objects.link(seismo_base)
    scene.collection.objects.unlink(seismo_base)
    
    # 纸带记录滚筒
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.8, location=(cx + 2.3, -0.4, 2.2))
    drum = bpy.context.active_object
    drum.rotation_euler = (math.radians(90), 0, 0)
    drum.data.materials.append(mats['WhiteLamp'])
    col_c.objects.link(drum)
    scene.collection.objects.unlink(drum)
    
    # 红色振动跳表指针
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.7, location=(cx + 2.05, -0.4, 2.25))
    needle = bpy.context.active_object
    needle.rotation_euler = (math.radians(90), 0, 0)
    needle.data.materials.append(mats['AlertRed'])
    col_c.objects.link(needle)
    scene.collection.objects.unlink(needle)
    
    # 探针剧烈跳动动画 (Frame 361 to 432, Shot 06)
    for f in range(361, 433, 3):
        needle.location = (cx + 2.05, -0.4 + (f % 5 - 2) * 0.18, 2.25)
        needle.keyframe_insert(data_path="location", frame=f)
        
    # 工作台荧光监视器
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx + 2.2, 1.1, 2.0))
    monitor = bpy.context.active_object
    monitor.scale = (0.1, 1.2, 0.7)
    monitor.data.materials.append(mats['XelNagaGlowBlue'])
    col_c.objects.link(monitor)
    scene.collection.objects.unlink(monitor)
    
    # 紧急警报红灯
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(cx, 0, 4.1))
    alert_lamp = bpy.context.active_object
    alert_lamp.data.materials.append(mats['AlertRed'])
    col_c.objects.link(alert_lamp)
    scene.collection.objects.unlink(alert_lamp)
    
    # 天花板晃动吊灯 (地震视觉标志)
    bpy.ops.object.empty_add(type='ARROWS', location=(cx, -1.0, 4.3))
    lamp_pivot = bpy.context.active_object
    lamp_pivot.name = "Lamp_Pivot"
    col_c.objects.link(lamp_pivot)
    scene.collection.objects.unlink(lamp_pivot)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1.6, location=(0, 0, -0.8))
    wire = bpy.context.active_object
    wire.parent = lamp_pivot
    wire.data.materials.append(mats['Treads'])
    col_c.objects.link(wire)
    scene.collection.objects.unlink(wire)
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.35, radius2=0.1, depth=0.3, location=(0, 0, -1.6))
    shade = bpy.context.active_object
    shade.parent = lamp_pivot
    shade.data.materials.append(mats['TurretOlive'])
    col_c.objects.link(shade)
    scene.collection.objects.unlink(shade)
    
    # 吊灯在地震镜头 (Frame 433 to 504, Shot 07) 中剧烈狂摆动画
    for f in range(433, 505, 4):
        sw_x = math.sin(f * 0.4) * math.radians(28)
        sw_y = math.cos(f * 0.3) * math.radians(22)
        lamp_pivot.rotation_euler = (sw_x, sw_y, 0)
        lamp_pivot.keyframe_insert(data_path="rotation_euler", frame=f)
        
    # 重型防风百叶窗降下锁死动画 (Frame 289 to 360, Shot 05)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, 3.45, 4.0))
    shutter = bpy.context.active_object
    shutter.scale = (2.6, 0.12, 1.8)
    shutter.data.materials.append(mats['Treads'])
    col_c.objects.link(shutter)
    scene.collection.objects.unlink(shutter)
    
    shutter.location = (cx, 3.45, 3.9)
    shutter.keyframe_insert(data_path="location", frame=289)
    shutter.location = (cx, 3.45, 2.3)
    shutter.keyframe_insert(data_path="location", frame=332)
    
    # 板房内的人体假人 (拉尔斯在工作台前俯身观察；奥克塔维亚在旁边抓住栏杆支撑)
    lars_inside = create_human_dummy("Lars_Inside", (cx + 1.2, -0.4, 0), rot_deg=(0,0,90), scale=0.95,
                                     suit_mat=mats['HumanSuitOrange'], skin_mat=mats['Skin'], col=col_c)
    octavia_inside = create_human_dummy("Octavia_Inside", (cx + 1.0, 0.8, 0), rot_deg=(0,0,105), scale=0.90,
                                       suit_mat=mats['HumanSuitBlue'], skin_mat=mats['Skin'], col=col_c)
    
    # 地震时人体晃动挣扎动画 (Frame 433 to 504)
    for f in range(433, 505, 4):
        lars_inside.rotation_euler = (math.sin(f*0.5)*math.radians(12), 0, math.radians(90))
        lars_inside.keyframe_insert(data_path="rotation_euler", frame=f)
        octavia_inside.rotation_euler = (math.cos(f*0.4)*math.radians(15), 0, math.radians(105))
        octavia_inside.keyframe_insert(data_path="rotation_euler", frame=f)

    # =========================================================================
    # SET E: 查尔星火山废土与刀锋女王王座 (X: 1300) -> Shot 08
    # =========================================================================
    col_e = bpy.data.collections.new("Set_E_PlanetChar")
    scene.collection.children.link(col_e)
    ex = 1300
    
    # 玄武岩地面
    bpy.ops.mesh.primitive_plane_add(size=160, location=(ex, 0, 0))
    c_ground = bpy.context.active_object
    c_ground.data.materials.append(mats['CharBasalt'])
    col_e.objects.link(c_ground)
    scene.collection.objects.unlink(c_ground)
    
    # 蜿蜒发光的火山熔岩裂谷
    for idx, (lx, ly, rot, length) in enumerate([(ex - 25, 10, 30, 80), (ex + 18, -25, -45, 90), (ex, 35, 12, 100)]):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(lx, ly, 0.15))
        lava = bpy.context.active_object
        lava.scale = (9.0, length, 0.25)
        lava.rotation_euler = (0, 0, math.radians(rot))
        lava.data.materials.append(mats['CharLava'])
        col_e.objects.link(lava)
        scene.collection.objects.unlink(lava)
        
    # 巨大的异虫螺旋尖塔 (Spire)
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=7.0, radius2=0.8, depth=65.0, location=(ex, 0, 32.5))
    main_spire = bpy.context.active_object
    main_spire.rotation_euler = (math.radians(6), math.radians(4), 0)
    main_spire.data.materials.append(mats['ZergPurple'])
    col_e.objects.link(main_spire)
    scene.collection.objects.unlink(main_spire)
    
    # 伴生副尖塔
    for s_idx, (sx, sy, sh) in enumerate([(ex - 28, 22, 45), (ex + 25, 18, 38)]):
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=4.5, radius2=0.5, depth=sh, location=(sx, sy, sh/2))
        sp = bpy.context.active_object
        sp.data.materials.append(mats['ZergPurple'])
        col_e.objects.link(sp)
        scene.collection.objects.unlink(sp)
        
    # 异虫几丁质主巢王座平台
    bpy.ops.mesh.primitive_cylinder_add(radius=5.0, depth=1.5, location=(ex, 0, 48.0))
    throne_plat = bpy.context.active_object
    throne_plat.data.materials.append(mats['ZergBone'])
    col_e.objects.link(throne_plat)
    scene.collection.objects.unlink(throne_plat)
    
    # 刀锋女王凯瑞甘高空剪影假人（带骨翼剪影）
    kerrigan_dummy = create_human_dummy("Kerrigan_QueenOfBlades", (ex, 0, 48.8), rot_deg=(0,0,180), scale=1.4,
                                        suit_mat=mats['ZergPurple'], skin_mat=mats['ZergBone'], col=col_e)
    # 骨质翅膀剪影
    for wing_side, wx in [(-1.2, -1), (1.2, 1)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.2, 1.4))
        wing = bpy.context.active_object
        wing.scale = (0.1, 1.5, 0.4)
        wing.rotation_euler = (math.radians(35), math.radians(wx * 30), math.radians(wx * 20))
        wing.parent = kerrigan_dummy
        wing.data.materials.append(mats['ZergBone'])
        col_e.objects.link(wing)
        scene.collection.objects.unlink(wing)

    # =========================================================================
    # SET D: 萨尔那加出土神庙裂谷与通天信标 (X: 850) -> Shot 09, Shot 10
    # =========================================================================
    col_d = bpy.data.collections.new("Set_D_XelNagaTemple_Chasm")
    scene.collection.children.link(col_d)
    dx = 850
    
    # 撕裂的地表与深达百米的悬崖断壁
    bpy.ops.mesh.primitive_plane_add(size=200, location=(dx, 0, 0))
    c_floor = bpy.context.active_object
    c_floor.data.materials.append(mats['Mud'])
    col_d.objects.link(c_floor)
    scene.collection.objects.unlink(c_floor)
    
    for side, y_off in [("North", -70), ("South", 70)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(dx, y_off, 45))
        cliff = bpy.context.active_object
        cliff.scale = (180, 50, 90)
        cliff.data.materials.append(mats['RockDark'])
        col_d.objects.link(cliff)
        scene.collection.objects.unlink(cliff)
        
    # 悬崖边缘对比比例尺道具：微型收割机与破碎栅栏 (瞬间凸显神庙雄伟尺度)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(dx - 35, 43, 90.8))
    tiny_harvester = bpy.context.active_object
    tiny_harvester.scale = (2.2, 4.2, 1.2)
    tiny_harvester.data.materials.append(mats['HarvesterRed'])
    col_d.objects.link(tiny_harvester)
    scene.collection.objects.unlink(tiny_harvester)
    
    # 5级梯形黑曜石金字塔神庙主体 (带发光能量回路)
    tiers = [
        (85, 85, 14, 7),
        (68, 68, 14, 21),
        (52, 52, 12, 34),
        (36, 36, 10, 45),
        (24, 24, 8, 54),
    ]
    for idx, (sx, sy, sz, cz) in enumerate(tiers):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(dx, 0, cz))
        t = bpy.context.active_object
        t.scale = (sx, sy, sz)
        t.data.materials.append(mats['XelNagaObsidian'])
        col_d.objects.link(t)
        scene.collection.objects.unlink(t)
        
        # 发光灵能导轨饰条
        bpy.ops.mesh.primitive_cube_add(size=1, location=(dx, 0, cz + sz/2 - 0.2))
        cg = bpy.context.active_object
        cg.scale = (sx + 0.6, sy + 0.6, 0.4)
        cg.data.materials.append(mats['XelNagaGlowBlue'])
        col_d.objects.link(cg)
        scene.collection.objects.unlink(cg)
        
    # 顶部金字塔祭坛核心晶体
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=6.0, radius2=0.0, depth=7.0, location=(dx, 0, 61.5))
    top_pyr = bpy.context.active_object
    top_pyr.rotation_euler = (0, 0, math.radians(45))
    top_pyr.data.materials.append(mats['XelNagaGlowBlue'])
    col_d.objects.link(top_pyr)
    scene.collection.objects.unlink(top_pyr)
    
    # 神庙正门：巨型三角结晶门廊 (Shot 10 特写舞台)
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=8.0, depth=2.5, location=(dx, 42.5, 9.0))
    door = bpy.context.active_object
    door.rotation_euler = (math.radians(90), 0, 0)
    door.data.materials.append(mats['XelNagaGlowBlue'])
    col_d.objects.link(door)
    scene.collection.objects.unlink(door)
    
    # 门前拉尔斯具象化人体假人 (Shot 10 主角)
    lars_sh10 = create_human_dummy("Lars_TempleSacrifice", (dx, 40.0, 0.0), rot_deg=(0,0,0), scale=1.05,
                                   suit_mat=mats['HumanSuitOrange'], skin_mat=mats['Skin'], col=col_d)
    
    # 关键帧动画：拉尔斯走向大门 -> 引力悬浮升空 -> 强光中粒子瓦解消散
    # 走向大门
    lars_sh10.location = (dx, 38.0, 0.0)
    lars_sh10.keyframe_insert(data_path="location", frame=673)
    lars_sh10.location = (dx, 41.2, 0.0)
    lars_sh10.keyframe_insert(data_path="location", frame=705)
    
    # 悬浮升空并在强光中张开双臂
    lars_sh10.location = (dx, 41.2, 4.5)
    lars_sh10.keyframe_insert(data_path="location", frame=730)
    
    # 身体在强光中分解为纯能量粒子群并消失
    lars_sh10.scale = (1.05, 1.05, 1.05)
    lars_sh10.keyframe_insert(data_path="scale", frame=730)
    lars_sh10.scale = (0.001, 0.001, 0.001)
    lars_sh10.keyframe_insert(data_path="scale", frame=742)
    
    # 扩散粒子群 (消散的能量视觉化)
    col_particles = []
    for p_i in range(12):
        ang = p_i * (2 * math.pi / 12)
        px = dx + math.cos(ang) * 0.5
        pz = 4.5 + math.sin(ang) * 0.5
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(px, 41.2, pz))
        pt = bpy.context.active_object
        pt.data.materials.append(mats['XelNagaGlowBlue'])
        col_d.objects.link(pt)
        scene.collection.objects.unlink(pt)
        col_particles.append((pt, math.cos(ang), math.sin(ang)))
        
        # 初始隐藏在身体内部
        pt.scale = (0.001, 0.001, 0.001)
        pt.keyframe_insert(data_path="scale", frame=725)
        # 爆发膨胀
        pt.scale = (1.8, 1.8, 1.8)
        pt.keyframe_insert(data_path="scale", frame=738)
        pt.location = (dx + math.cos(ang) * 5.0, 41.2, 4.5 + math.sin(ang) * 5.0)
        pt.keyframe_insert(data_path="location", frame=745)
        pt.scale = (0.001, 0.001, 0.001)
        pt.keyframe_insert(data_path="scale", frame=750)
        
    # 400米宇宙纯能信标光柱 (自神庙顶端轰然冲上云霄)
    bpy.ops.mesh.primitive_cylinder_add(radius=5.5, depth=450.0, location=(dx, 0, -250))
    beam = bpy.context.active_object
    beam.data.materials.append(mats['BeaconBeam'])
    col_d.objects.link(beam)
    scene.collection.objects.unlink(beam)
    
    beam.location = (dx, 0, -250)
    beam.keyframe_insert(data_path="location", frame=735)
    beam.location = (dx, 0, 275)
    beam.keyframe_insert(data_path="location", frame=755)
    
    # 宇宙信标扩散冲击波环 (大气层撕裂效果)
    for r_idx, (r_rad, r_z) in enumerate([(30.0, 140.0), (60.0, 220.0), (100.0, 320.0)]):
        bpy.ops.mesh.primitive_torus_add(major_radius=r_rad, minor_radius=2.0, location=(dx, 0, r_z))
        ring = bpy.context.active_object
        ring.data.materials.append(mats['BeaconBeam'])
        col_d.objects.link(ring)
        scene.collection.objects.unlink(ring)
        
        ring.scale = (0.01, 0.01, 0.01)
        ring.keyframe_insert(data_path="scale", frame=740 + r_idx * 14)
        ring.scale = (2.2, 2.2, 2.2)
        ring.keyframe_insert(data_path="scale", frame=780 + r_idx * 14)

def setup_timeline_cameras():
    scene = bpy.context.scene
    col_cam = bpy.data.collections.new("Cameras_Animatic")
    scene.collection.children.link(col_cam)
    
    def create_cam(name, loc, rot_deg, lens=35.0):
        cdata = bpy.data.cameras.new(name)
        cdata.lens = lens
        cdata.clip_end = 3000.0
        cobj = bpy.data.objects.new(name, cdata)
        cobj.location = loc
        cobj.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
        col_cam.objects.link(cobj)
        return cobj

    def bind_marker(name, frame, cam_obj):
        marker = scene.timeline_markers.new(name, frame=frame)
        marker.camera = cam_obj
        return marker

    # 1. Shot 01 (Frame 1-72): 麦原风暴慢摇 (24mm)
    cam01 = create_cam("Cam_01_StormWide", (0, 36, 1.8), (80, 0, 180), lens=24.0)
    cam01.rotation_euler = (math.radians(78), 0, math.radians(180))
    cam01.keyframe_insert(data_path="rotation_euler", frame=1)
    cam01.rotation_euler = (math.radians(85), 0, math.radians(180))
    cam01.keyframe_insert(data_path="rotation_euler", frame=72)
    bind_marker("Shot01_StormWide", 1, cam01)
    
    # 2. Shot 02 (Frame 73-144): 侧后45°高速跟拍收割机 (35mm)
    cam02 = create_cam("Cam_02_HarvesterTrack", (-11, 42, 4.5), (76, 0, -145), lens=35.0)
    cam02.location = (-11, 44, 4.5)
    cam02.keyframe_insert(data_path="location", frame=73)
    cam02.location = (-11, -12, 4.5)
    cam02.keyframe_insert(data_path="location", frame=144)
    bind_marker("Shot02_HarvesterTrack", 73, cam02)
    
    # 3. Shot 03 (Frame 145-216): 驾驶舱颠簸特写与地平线剧烈起伏 (28mm)
    cam03 = create_cam("Cam_03_CockpitMS", (0, 0.4, 3.5), (90, 0, 0), lens=28.0)
    for f in range(145, 217, 3):
        shake = (f % 4 - 2) * 0.045
        cam03.location = (shake, 0.4, 3.5 + shake)
        cam03.keyframe_insert(data_path="location", frame=f)
    bind_marker("Shot03_CockpitMS", 145, cam03)
    
    # 4. Shot 04 (Frame 217-288): 自由避难所防风圈与旧导弹塔仰望 (35mm)
    cam05 = create_cam("Cam_05_TurretPerimeter", (244, 2, 2.2), (70, 0, -25), lens=35.0)
    cam05.location = (244, 2, 2.2)
    cam05.keyframe_insert(data_path="location", frame=217)
    cam05.location = (242, 6, 2.8)
    cam05.keyframe_insert(data_path="location", frame=288)
    bind_marker("Shot04_TurretPerimeter", 217, cam05)
    
    # 5. Shot 05 (Frame 289-360): 室内避难所合力锁窗 (24mm)
    cam07 = create_cam("Cam_07_HomesteadLock", (497.5, -2.2, 2.4), (78, 0, 30), lens=24.0)
    bind_marker("Shot05_HomesteadLock", 289, cam07)
    
    # 6. Shot 06 (Frame 361-432): 地震仪跳表爆表长焦大特写 (70mm)
    cam09 = create_cam("Cam_09_SeismographECU", (501.0, -0.4, 2.25), (90, 0, -90), lens=70.0)
    for f in range(361, 433, 4):
        cam09.location = (501.0 + (f%3-1)*0.015, -0.4 + (f%2-1)*0.015, 2.25)
        cam09.keyframe_insert(data_path="location", frame=f)
    bind_marker("Shot06_SeismographECU", 361, cam09)
    
    # 7. Shot 07 (Frame 433-504): 大地震剧烈晃动，吊灯狂摆与红光断电 (35mm)
    cam10 = create_cam("Cam_10_HomesteadQuake", (498.2, 0.4, 2.3), (85, 0, 70), lens=35.0)
    for f in range(433, 505, 2):
        q = (f % 5 - 2) * 0.14
        cam10.location = (498.2 + q, 0.4 + q*0.5, 2.3 + q*0.8)
        cam10.keyframe_insert(data_path="location", frame=f)
    bind_marker("Shot07_HomesteadQuake", 433, cam10)
    
    # 8. Shot 08 (Frame 505-576): 查尔星火山异虫主巢俯瞰与刀锋女王 (24mm)
    cam12 = create_cam("Cam_12_CharHive", (1300, 70, 52), (54, 0, 180), lens=24.0)
    cam12.location = (1300, 80, 56)
    cam12.keyframe_insert(data_path="location", frame=505)
    cam12.location = (1300, 52, 46)
    cam12.keyframe_insert(data_path="location", frame=576)
    bind_marker("Shot08_CharHive", 505, cam12)
    
    # 9. Shot 09 (Frame 577-672): 萨尔那加出土金字塔裂谷大俯冲与微型收割机 (18mm)
    cam15 = create_cam("Cam_15_TempleChasmEpic", (850, 155, 105), (58, 0, 180), lens=18.0)
    cam15.location = (850, 165, 115)
    cam15.keyframe_insert(data_path="location", frame=577)
    cam15.location = (850, 105, 62)
    cam15.keyframe_insert(data_path="location", frame=672)
    bind_marker("Shot09_TempleChasmEpic", 577, cam15)
    
    # 10. Shot 10 (Frame 673-792): 拉尔斯触碰大门、强光粒子化与400米宇宙信标爆发 (16mm)
    cam19 = create_cam("Cam_19_CosmicBeacon", (850, 22.0, 3.2), (48, 0, 0), lens=16.0)
    cam19.rotation_euler = (math.radians(45), 0, 0)
    cam19.keyframe_insert(data_path="rotation_euler", frame=673)
    cam19.rotation_euler = (math.radians(18), 0, 0)
    cam19.keyframe_insert(data_path="rotation_euler", frame=792)
    bind_marker("Shot10_CosmicBeacon", 673, cam19)

# 镜头导演解说字幕数据库 (镜头编号、名称、机位焦段、剧情动作说明、视听提示)
SHOT_CAPTIONS = {
    (1, 72): {
        "title": "SHOT 01 / 10 | 贝卡·罗麦原 · 激光风暴远景慢摇",
        "lens": "24mm 广角慢摇 | 广袤麦田平原与电闪雷鸣",
        "action": "【剧情调度】黄昏的麦原被异星激光风暴笼罩，闪电劈向地平线，一辆重型联合收割机正冒烟狂奔。",
        "intent": "【视听意图】建立极端末日生存环境，孤立微弱的人类科技对抗浩瀚毁灭性自然风暴。"
    },
    (73, 144): {
        "title": "SHOT 02 / 10 | 联合收割机 · 侧后 45° 高速追随跟拍",
        "lens": "35mm 中景跟拍 | 45° 侧后视线低机位",
        "action": "【剧情调度】巨型履带飞溅翻滚泥土，前置收割滚筒高速切割麦秆，拉尔斯与妹妹争分夺秒撤离。",
        "intent": "【视听意图】强烈的工业机械厚重感与风暴追击的速度压迫感。"
    },
    (145, 216): {
        "title": "SHOT 03 / 10 | 驾驶舱内景 · 兄妹颠簸特写与起伏地平线",
        "lens": "28mm 颠簸中景 | 驾驶室逼仄空间手持感",
        "action": "【剧情调度】车体剧烈震颤。拉尔斯双手死死把住方向盘，副驾奥克塔维亚焦急地注视跳动仪表盘。",
        "intent": "【视听意图】近距离展现人类角色的恐慌与坚毅，地平线在车窗外剧烈颠簸。"
    },
    (217, 288): {
        "title": "SHOT 04 / 10 | 避难所防风圈 · 老式双联导弹塔锁定天际",
        "lens": "35mm 仰视推进 | 避难所防御圈与冷战工业风",
        "action": "【剧情调度】收割机冲入八角形防风堤。老式双联防空导弹塔旋转雷达天线，导弹发射架指向电光云层。",
        "intent": "【视听意图】Terran 殖民地拓荒定居点的简陋防御，凸显殖民者在恶劣边陲的脆弱武装。"
    },
    (289, 360): {
        "title": "SHOT 05 / 10 | 活动板房内景 · 兄妹合力关闭防风重型百叶窗",
        "lens": "24mm 室内全景 | 紧闭窗户隔绝外部风暴",
        "action": "【剧情调度】兄妹两人冲入预制板房。厚重的金属防风百叶窗重重滑落锁死，隔绝窗外的雷暴强光。",
        "intent": "【视听意图】从狂暴外部环境瞬间转入幽闭安全感，但危险即将在地底引爆。"
    },
    (361, 432): {
        "title": "SHOT 06 / 10 | 兄妹工作台 · 简易地震仪指针剧烈打到爆表特写",
        "lens": "70mm 长焦微距特写 | 地震仪纸带记录滚筒与指针",
        "action": "【剧情调度】原本平稳的自制地震仪纸带突然剧烈颤动，红色指针瞬间撞击量程极限，地底深处震动！",
        "intent": "【视听意图】未知危机的第一个信号，极小道具撬动整个星球维度的宏大灾变悬念。"
    },
    (433, 504): {
        "title": "SHOT 07 / 10 | 板房大地震 · 吊灯狂摆、室内倾斜与警报断电",
        "lens": "35mm 剧烈手持晃动 | 8.5级罕见大地震爆发",
        "action": "【剧情调度】大地震爆发！房顶吊灯疯狂甩荡，工作台器械翻倒，应急红灯狂闪，兄妹两人死死抓牢桌沿支撑。",
        "intent": "【视听意图】直观的地震灾难视效，将危机推向物理层面的最高潮。"
    },
    (505, 576): {
        "title": "SHOT 08 / 10 | 查尔星火山主巢 · 刀锋女王凯瑞甘感应灵能共振",
        "lens": "24mm 大角度俯冲 | 异虫母星玄武岩与熔岩废土",
        "action": "【剧情调度】【星际跨星系切镜】神庙脉冲穿透光年。刀锋女王感应到萨尔那加灵能共振，几丁质尖塔共振低鸣。",
        "intent": "【视听意图】视听格局瞬间跃迁到全星系势力对抗，揭示出土古物的宇宙级危险性。"
    },
    (577, 672): {
        "title": "SHOT 09 / 10 | 农场大裂谷深处 · 萨尔那加黑曜石神庙出土",
        "lens": "18mm 超广角史诗俯冲 | 裂谷深处百米金字塔神庙",
        "action": "【剧情调度】麦原撕开万丈深渊！悬崖边缘微小的收割机印衬出深渊下方沉睡万年的黑曜石金字塔神庙出土！",
        "intent": "【视听意图】强烈的超自然宇宙尺度震撼，古代高等造物主文明的肃穆与神秘力量。"
    },
    (673, 792): {
        "title": "SHOT 10 / 10 | 神庙核心大门 · 拉尔斯粒子化与400米宇宙信标爆发",
        "lens": "16mm 极致仰拍 | 结晶大门、引力瓦解与宇宙信标",
        "action": "【剧情调度】拉尔斯触碰三角结晶大门，被反重力悬浮并在强光中瓦解为纯能量粒子；400米信标光柱撕裂大气层刺入深空！",
        "intent": "【视听意图】第一幕终局事件：信标激活，星灵黄金舰队与异虫大军已全数调转航向扑向贝卡·罗！"
    }
}

def get_caption_for_frame(frame_num):
    for (start_f, end_f), cap in SHOT_CAPTIONS.items():
        if start_f <= frame_num <= end_f:
            return cap
    return None

def compile_frames_with_director_hud(frames_dir, output_mp4, fps=24.0, width=1920, height=804):
    """
    使用 PIL + OpenCV 为每一帧添加电影级导演监视器 HUD 与解说字幕，彻底消除抽象感
    """
    frame_files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.png")))
    total_frames = len(frame_files)
    if total_frames == 0:
        raise RuntimeError(f"No frames found in {frames_dir} to compile video!")
        
    print(f"[Platform/Blender] Compiling {total_frames} frames with Director HUD into: {output_mp4} ...")
    
    # 加载系统优质微软雅黑字体
    font_path = "C:/Windows/Fonts/msyh.ttc"
    font_title = ImageFont.truetype(font_path, 28)
    font_sub = ImageFont.truetype(font_path, 20)
    font_tc = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 22)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_dir = os.path.dirname(output_mp4)
    os.makedirs(out_dir, exist_ok=True)
    
    writer = cv2.VideoWriter(output_mp4, fourcc, fps, (width, height))
    
    for idx, fpath in enumerate(frame_files):
        frame_num = idx + 1
        img_bgr = cv2.imread(fpath)
        if img_bgr is None:
            continue
        if img_bgr.shape[1] != width or img_bgr.shape[0] != height:
            img_bgr = cv2.resize(img_bgr, (width, height))
            
        # 转换为 RGBA 图像以绘制半透明 HUD
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb).convert('RGBA')
        
        # 叠加透明层
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # 1. 顶部极窄时间码栏 (Top Bar)
        draw.rectangle([(0, 0), (width, 42)], fill=(15, 18, 22, 210))
        
        # 计算时间码 TC 00:00:SS:FF
        sec = int(frame_num / fps)
        rem_f = int(frame_num % fps)
        tc_str = f"TC 00:00:{sec:02d}:{rem_f:02d} | FRAME {frame_num:03d}/{total_frames} | 24 FPS"
        draw.text((35, 8), tc_str, font=font_tc, fill=(160, 210, 255, 255))
        draw.text((width - 450, 8), "STARCRAFT: SHADOW OF THE XEL'NAGA - PREVIS", font=font_tc, fill=(200, 200, 200, 220))
        
        # 2. 底部电影级解说字幕条 (Bottom Director HUD)
        cap = get_caption_for_frame(frame_num)
        if cap:
            hud_h = 135
            draw.rectangle([(0, height - hud_h), (width, height)], fill=(12, 14, 18, 225))
            # 顶部装饰高亮金线
            draw.line([(0, height - hud_h), (width, height - hud_h)], fill=(255, 195, 0, 180), width=2)
            
            # 第一行：镜头编号与机位焦段 (金色高亮)
            draw.text((45, height - 124), f"🎬 {cap['title']}", font=font_title, fill=(255, 215, 0, 255))
            draw.text((width - 420, height - 120), cap['lens'], font=font_sub, fill=(130, 200, 255, 240))
            
            # 第二行：剧情动作说明 (纯白清晰)
            draw.text((45, height - 82), cap['action'], font=font_sub, fill=(245, 245, 245, 255))
            
            # 第三行：视听导演意图 (柔和浅灰)
            draw.text((45, height - 48), cap['intent'], font=font_sub, fill=(175, 185, 195, 240))
            
        # 合并图像并转回 BGR 供 cv2 写入
        combined = Image.alpha_composite(pil_img, overlay).convert('RGB')
        frame_out = cv2.cvtColor(np.array(combined), cv2.COLOR_RGB2BGR)
        writer.write(frame_out)
        
        if frame_num % 100 == 0 or frame_num == total_frames:
            print(f"[Platform/Blender] Encoded frame with HUD {frame_num}/{total_frames} ({(frame_num) / total_frames * 100:.1f}%)")
            
    writer.release()
    print(f"[Platform/Blender] SUCCESS: Enhanced Previs video saved at {output_mp4}")

def main():
    task_root = r"D:\nano-video-studio\tasks\blender\previs-blocking-act-001"
    work_dir = os.path.join(task_root, "work")
    output_dir = os.path.join(task_root, "output")
    frames_dir = os.path.join(work_dir, "frames")
    
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(frames_dir, exist_ok=True)
    
    # 1. 场景配置与具象化几何体搭建
    scene = setup_video_scene(frames_dir)
    mats = build_materials()
    build_sets_and_animations(mats)
    setup_timeline_cameras()
    
    # 2. 保存工作工程至 tasks/blender/<task-id>/work/previs_act01_video.blend
    work_blend = os.path.join(work_dir, "previs_act01_video.blend")
    bpy.ops.wm.save_as_mainfile(filepath=work_blend)
    print(f"[Platform/Blender] SUCCESS: Saved enhanced work .blend to {work_blend}")
    
    # 3. 运行动画帧序列渲染
    print(f"[Platform/Blender] START RENDER: Rendering {scene.frame_start} to {scene.frame_end} frames...")
    bpy.ops.render.render(animation=True)
    print(f"[Platform/Blender] RENDER FINISHED. All frames saved to {frames_dir}")
    
    # 4. 逐帧合成电影级导演 HUD 与详细解说字幕导出 MP4
    output_video = os.path.join(output_dir, "previs_act01_animatic.mp4")
    compile_frames_with_director_hud(frames_dir, output_video, fps=24.0, width=1920, height=804)
    
    # 5. 清理临时帧缓存
    for f in glob.glob(os.path.join(frames_dir, "frame_*.png")):
        try:
            os.remove(f)
        except:
            pass
    try:
        os.rmdir(frames_dir)
    except:
        pass
    print("[Platform/Blender] Cleaned up temporary frames cache.")

if __name__ == "__main__":
    main()

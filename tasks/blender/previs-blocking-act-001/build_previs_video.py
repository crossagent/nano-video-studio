"""
tasks/blender/previs-blocking-act-001/build_previs_video.py
《星际争霸：萨尔那加之影》第一幕 3D 白模分镜动画预演（Previs 3.0 影视级具象建模版）
重构亮点：
1. 【高精具象化仪器设备】Shot 06 地震仪彻底重构为真实工业/科幻记录仪：
   - 带有精工斜面机箱、双联圆形模拟量程表头（刻度指针）；
   - 旋转走纸记录滚筒、双侧金属轴承座与滚轴传动机构；
   - 铰接式机械画笔悬臂与红墨尖头（关键帧高频大幅摆动）；
   - 荧光波形示波器屏幕、旋钮、拨动开关与红黄绿三色状态指示灯；
   - 场景中加入操作员手臂与手掌悬于台面，确立人机操作关系。
2. 【全场景精细化环境与道具建模】：
   - 板房工作台：增加虎钳工具、翻倒的保温杯（地震时滑落）、操作电台与天线；
   - 晃动工业吊灯：金属链条悬吊、带防撞金属防护网罩的工业吊灯，地震时大角度狂甩；
   - 联合收割机：前置液压支撑架、分禾齿梳、双排履带导向轮、排气烟囱与驾驶室防滚架；
   - 防空导弹塔：八角形底座、液压回转俯仰台、双联装8管带开孔导弹舱、旋转雷达网架；
   - 查尔星异虫主巢：螺旋几丁质利角尖塔、孵化卵囊群、熔岩断层、刀锋女王凯瑞甘骨翼发辫剪影；
   - 出土萨尔那加神庙：阶梯式巨石金字塔、中央登神阶梯、悬浮菱形核心晶体、边缘微缩收割机比例尺；
   - 宇宙信标爆发：拉尔斯悬浮张臂分解为24颗向外喷射的能量碎片，通天主光柱+双螺旋缠绕能量环+4重大气激波扩散环。
3. 【电影级导演监视器 HUD 与解说字幕】：逐帧压制镜头编号、机位焦段、剧情调度说明与视听意图。
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
    shading.cavity_ridge_factor = 2.2
    shading.cavity_valley_factor = 1.6
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
    mats['RockDark'] = create_mat('Mat_RockDark', (0.18, 0.18, 0.20, 1.0), roughness=0.85)
    mats['HarvesterRed'] = create_mat('Mat_HarvesterRed', (0.76, 0.14, 0.16, 1.0), roughness=0.35, metallic=0.3)
    mats['Treads'] = create_mat('Mat_Treads', (0.11, 0.11, 0.13, 1.0), roughness=0.7, metallic=0.85)
    mats['SteelPolished'] = create_mat('Mat_SteelPolished', (0.80, 0.82, 0.85, 1.0), roughness=0.25, metallic=0.9)
    mats['BrassGold'] = create_mat('Mat_BrassGold', (0.85, 0.68, 0.22, 1.0), roughness=0.3, metallic=0.8)
    mats['GlassCyan'] = create_mat('Mat_GlassCyan', (0.35, 0.85, 0.95, 0.8), roughness=0.1, metallic=0.1)
    mats['MetalRust'] = create_mat('Mat_MetalRust', (0.42, 0.26, 0.18, 1.0), roughness=0.75, metallic=0.45)
    mats['TurretOlive'] = create_mat('Mat_TurretOlive', (0.28, 0.34, 0.22, 1.0), roughness=0.55, metallic=0.5)
    mats['ConsoleCasing'] = create_mat('Mat_ConsoleCasing', (0.15, 0.17, 0.20, 1.0), roughness=0.4, metallic=0.7)
    mats['PaperGrid'] = create_mat('Mat_PaperGrid', (0.95, 0.94, 0.90, 1.0), roughness=0.85)
    mats['XelNagaObsidian'] = create_mat('Mat_XelNagaObsidian', (0.04, 0.05, 0.07, 1.0), roughness=0.2, metallic=0.95)
    mats['XelNagaGlowBlue'] = create_mat('Mat_XelNagaGlowBlue', (0.1, 0.82, 1.0, 1.0), emission_color=(0.1, 0.82, 1.0, 1.0), emission_strength=8.0)
    mats['BeaconBeam'] = create_mat('Mat_BeaconBeam', (0.92, 0.98, 1.0, 1.0), emission_color=(0.92, 0.98, 1.0, 1.0), emission_strength=20.0)
    mats['CharBasalt'] = create_mat('Mat_CharBasalt', (0.07, 0.06, 0.08, 1.0), roughness=0.92)
    mats['CharLava'] = create_mat('Mat_CharLava', (1.0, 0.28, 0.01, 1.0), emission_color=(1.0, 0.28, 0.01, 1.0), emission_strength=12.0)
    mats['ZergPurple'] = create_mat('Mat_ZergPurple', (0.32, 0.11, 0.38, 1.0), roughness=0.3)
    mats['ZergBone'] = create_mat('Mat_ZergBone', (0.68, 0.63, 0.50, 1.0), roughness=0.35)
    mats['HumanSuitOrange'] = create_mat('Mat_HumanSuitOrange', (0.82, 0.40, 0.14, 1.0), roughness=0.5)
    mats['HumanSuitBlue'] = create_mat('Mat_HumanSuitBlue', (0.22, 0.36, 0.56, 1.0), roughness=0.5)
    mats['Skin'] = create_mat('Mat_Skin', (0.86, 0.70, 0.60, 1.0), roughness=0.6)
    mats['AlertRed'] = create_mat('Mat_AlertRed', (1.0, 0.05, 0.05, 1.0), emission_color=(1.0, 0.05, 0.05, 1.0), emission_strength=14.0)
    mats['StatusGreen'] = create_mat('Mat_StatusGreen', (0.1, 1.0, 0.2, 1.0), emission_color=(0.1, 1.0, 0.2, 1.0), emission_strength=8.0)
    mats['StatusYellow'] = create_mat('Mat_StatusYellow', (1.0, 0.85, 0.1, 1.0), emission_color=(1.0, 0.85, 0.1, 1.0), emission_strength=8.0)
    mats['WhiteLamp'] = create_mat('Mat_WhiteLamp', (1.0, 1.0, 0.95, 1.0), emission_color=(1.0, 1.0, 0.95, 1.0), emission_strength=10.0)
    return mats

def create_human_dummy(name, loc, rot_deg=(0,0,0), scale=1.0, suit_mat=None, skin_mat=None, parent=None, col=None):
    """
    创建结构清晰、辨识度极高的人形模特：安全头盔、面罩、躯干胸甲、战术腰带、活动手臂、手掌、大腿小腿
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
    
    # 躯干胸甲 (0.42m x 0.28m x 0.55m)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.25))
    torso = bpy.context.active_object
    torso.scale = (0.42, 0.28, 0.55)
    torso.parent = root
    if suit_mat: torso.data.materials.append(suit_mat)
    parts.append(torso)
    
    # 头部/安全头盔 (Sphere 0.19m)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.19, location=(0, 0, 1.74))
    head = bpy.context.active_object
    head.parent = root
    if skin_mat: head.data.materials.append(skin_mat)
    parts.append(head)
    
    # 护目镜面罩指示条
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.15, 1.75))
    visor = bpy.context.active_object
    visor.scale = (0.24, 0.08, 0.10)
    visor.parent = root
    if suit_mat: visor.data.materials.append(suit_mat)
    parts.append(visor)
    
    # 战术腰带
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.95))
    belt = bpy.context.active_object
    belt.scale = (0.44, 0.30, 0.10)
    belt.parent = root
    if suit_mat: belt.data.materials.append(suit_mat)
    parts.append(belt)
    
    # 手臂与手掌、双腿
    for side, sx in [('L', -0.32), ('R', 0.32)]:
        # 大臂
        bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.36, location=(sx, 0, 1.30))
        uarm = bpy.context.active_object
        uarm.parent = root
        if suit_mat: uarm.data.materials.append(suit_mat)
        parts.append(uarm)
        
        # 前臂
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.34, location=(sx, 0.08, 0.98))
        forearm = bpy.context.active_object
        forearm.parent = root
        if suit_mat: forearm.data.materials.append(suit_mat)
        parts.append(forearm)
        
        # 手掌
        bpy.ops.mesh.primitive_cube_add(size=1, location=(sx, 0.14, 0.78))
        hand = bpy.context.active_object
        hand.scale = (0.08, 0.12, 0.08)
        hand.parent = root
        if skin_mat: hand.data.materials.append(skin_mat)
        parts.append(hand)
        
        # 腿部
        bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.88, location=(sx * 0.55, 0, 0.46))
        leg = bpy.context.active_object
        leg.parent = root
        if suit_mat: leg.data.materials.append(suit_mat)
        parts.append(leg)
        
    for p in parts:
        if col:
            col.objects.link(p)
            scene.collection.objects.unlink(p)
            
    return root

def create_realistic_seismograph(name, loc, rot_deg=(0,0,0), scale=1.0, mats=None, parent=None, col=None):
    """
    影视级具象化地震记录仪（图纸滚筒、微型摆臂、双量程表头、波形示波器屏幕、旋钮、开关、状态灯）
    """
    scene = bpy.context.scene
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
    root.scale = (scale, scale, scale)
    if parent: root.parent = parent
    if col: col.objects.link(root)
    else: scene.collection.objects.link(root)
    
    parts = []
    
    # 1. 重型仪器下机箱底座 (带侧向散热格栅)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.22))
    base = bpy.context.active_object
    base.scale = (0.90, 1.30, 0.44)
    base.parent = root
    base.data.materials.append(mats['ConsoleCasing'])
    parts.append(base)
    
    # 底座四角防震橡胶脚垫
    for fx in [-0.40, 0.40]:
        for fy in [-0.58, 0.58]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.06, location=(fx, fy, -0.01))
            foot = bpy.context.active_object
            foot.parent = root
            foot.data.materials.append(mats['Treads'])
            parts.append(foot)
            
    # 2. 前置倾斜操作面板 (30度倒角)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.34, 0, 0.38))
    slant_deck = bpy.context.active_object
    slant_deck.scale = (0.28, 1.20, 0.36)
    slant_deck.rotation_euler = (0, math.radians(-32), 0)
    slant_deck.parent = root
    slant_deck.data.materials.append(mats['ConsoleCasing'])
    parts.append(slant_deck)
    
    # 3. 双联圆形模拟指针量程表头 (里氏震级与地质电流表)
    for g_idx, gy in enumerate([-0.36, -0.10]):
        # 表框
        bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.04, location=(0.42, gy, 0.44))
        gauge_rim = bpy.context.active_object
        gauge_rim.rotation_euler = (0, math.radians(58), 0)
        gauge_rim.parent = root
        gauge_rim.data.materials.append(mats['BrassGold'])
        parts.append(gauge_rim)
        
        # 白色表盘
        bpy.ops.mesh.primitive_cylinder_add(radius=0.085, depth=0.02, location=(0.43, gy, 0.445))
        dial = bpy.context.active_object
        dial.rotation_euler = (0, math.radians(58), 0)
        dial.parent = root
        dial.data.materials.append(mats['PaperGrid'])
        parts.append(dial)
        
        # 黑色/红色微型刻度指针
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0.44, gy, 0.45))
        g_needle = bpy.context.active_object
        g_needle.scale = (0.005, 0.07, 0.008)
        g_needle.rotation_euler = (math.radians(-35 + g_idx * 50), math.radians(58), 0)
        g_needle.parent = root
        g_needle.data.materials.append(mats['AlertRed'])
        parts.append(g_needle)
        
    # 4. 阴极射线示波管 / LCD 波形监视屏幕 (带发光地震波形)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.41, 0.28, 0.43))
    crt = bpy.context.active_object
    crt.scale = (0.04, 0.40, 0.20)
    crt.rotation_euler = (0, math.radians(-32), 0)
    crt.parent = root
    crt.data.materials.append(mats['XelNagaGlowBlue'])
    parts.append(crt)
    
    # 5. 状态指示灯阵列 (红/黄/绿)
    for l_idx, (col_name, ly) in enumerate([('StatusGreen', 0.12), ('StatusYellow', 0.18), ('AlertRed', 0.24)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.04, location=(0.42, ly, 0.56))
        led = bpy.context.active_object
        led.rotation_euler = (0, math.radians(58), 0)
        led.parent = root
        led.data.materials.append(mats[col_name])
        parts.append(led)
        
    # 6. 金属拨动开关与旋钮
    for k_idx, ky in enumerate([-0.45, -0.28, 0.46, 0.52]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.05, location=(0.40, ky, 0.28))
        knob = bpy.context.active_object
        knob.rotation_euler = (0, math.radians(58), 0)
        knob.parent = root
        knob.data.materials.append(mats['SteelPolished'])
        parts.append(knob)
        
    # 7. 后置旋转走纸记录滚筒组件 (Seismograph Recording Drum Assembly)
    # 滚筒左右金属轴承支架 (Bearing Brackets)
    for b_side, by in [('L', -0.42), ('R', 0.42)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.10, by, 0.60))
        bracket = bpy.context.active_object
        bracket.scale = (0.16, 0.05, 0.40)
        bracket.parent = root
        bracket.data.materials.append(mats['TurretOlive'])
        parts.append(bracket)
        
    # 贯穿钢轴 (Steel Central Shaft)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.98, location=(-0.10, 0, 0.66))
    shaft = bpy.context.active_object
    shaft.rotation_euler = (math.radians(90), 0, 0)
    shaft.parent = root
    shaft.data.materials.append(mats['SteelPolished'])
    parts.append(shaft)
    
    # 白色走纸圆柱滚筒主体 (Main Recording Drum with Grid Paper)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.74, location=(-0.10, 0, 0.66))
    paper_drum = bpy.context.active_object
    paper_drum.rotation_euler = (math.radians(90), 0, 0)
    paper_drum.parent = root
    paper_drum.name = f"{name}_PaperDrum"
    paper_drum.data.materials.append(mats['PaperGrid'])
    parts.append(paper_drum)
    
    # 滚筒表面纸张网格刻度环 (增加真实感细节)
    for ring_y in [-0.28, -0.14, 0.0, 0.14, 0.28]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.222, minor_radius=0.006, location=(-0.10, ring_y, 0.66))
        grid_ring = bpy.context.active_object
        grid_ring.rotation_euler = (0, math.radians(90), 0)
        grid_ring.parent = paper_drum
        grid_ring.data.materials.append(mats['RockDark'])
        parts.append(grid_ring)
        
    # 滚筒驱动齿轮箱 (Left Gear Box)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.10, location=(-0.10, -0.44, 0.66))
    gear_box = bpy.context.active_object
    gear_box.rotation_euler = (math.radians(90), 0, 0)
    gear_box.parent = root
    gear_box.data.materials.append(mats['BrassGold'])
    parts.append(gear_box)
    
    # 8. 铰接式机械画笔悬臂与红墨尖头 (Galvanometer Stylus Arm Assembly)
    # 电流检流计旋转底座轴心
    bpy.ops.object.empty_add(type='ARROWS', location=(0.18, 0, 0.64))
    stylus_pivot = bpy.context.active_object
    stylus_pivot.name = f"{name}_StylusPivot"
    stylus_pivot.parent = root
    
    # 检流计磁钢圆筒
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.14, location=(0.18, 0, 0.58))
    galvo = bpy.context.active_object
    galvo.parent = root
    galvo.data.materials.append(mats['ConsoleCasing'])
    parts.append(galvo)
    
    # 配重尾杆 (Counterweight Bar)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.12, location=(0.24, 0, 0.64))
    c_weight = bpy.context.active_object
    c_weight.rotation_euler = (0, math.radians(90), 0)
    c_weight.parent = stylus_pivot
    c_weight.data.materials.append(mats['BrassGold'])
    parts.append(c_weight)
    
    # 金属细悬臂 (Thin Metallic Cantilever Arm Extending to Drum)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.010, depth=0.28, location=(0.04, 0, 0.66))
    stylus_rod = bpy.context.active_object
    stylus_rod.rotation_euler = (0, math.radians(82), 0)
    stylus_rod.parent = stylus_pivot
    stylus_rod.data.materials.append(mats['SteelPolished'])
    parts.append(stylus_rod)
    
    # 红色微型墨水笔头 (Red Pen Tip Touching the Paper)
    bpy.ops.mesh.primitive_cone_add(radius1=0.018, radius2=0.002, depth=0.05, location=(-0.09, 0, 0.68))
    pen_tip = bpy.context.active_object
    pen_tip.rotation_euler = (0, math.radians(-75), 0)
    pen_tip.parent = stylus_pivot
    pen_tip.name = f"{name}_PenTip"
    pen_tip.data.materials.append(mats['AlertRed'])
    parts.append(pen_tip)
    
    # 9. 仪器后方波纹电源与传感器电缆
    for c_idx, cy in enumerate([-0.25, 0.25]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.60, location=(-0.45, cy, 0.15))
        cable = bpy.context.active_object
        cable.rotation_euler = (math.radians(20), math.radians(80), 0)
        cable.parent = root
        cable.data.materials.append(mats['Treads'])
        parts.append(cable)
        
    for p in parts:
        if col:
            col.objects.link(p)
            scene.collection.objects.unlink(p)
            
    return root, stylus_pivot, paper_drum

def build_sets_and_animations(mats):
    scene = bpy.context.scene
    
    # =========================================================================
    # SET A: 贝卡·罗麦田平原与联合收割机 (X: 0) -> Shot 01, Shot 02, Shot 03
    # =========================================================================
    col_a = bpy.data.collections.new("Set_A_BhekarRo_Plains")
    scene.collection.children.link(col_a)
    
    # 麦田地面与山脉
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
    bpy.ops.object.empty_add(type='ARROWS', location=(0, 36, 0))
    harvester_root = bpy.context.active_object
    harvester_root.name = "Harvester_Root"
    col_a.objects.link(harvester_root)
    scene.collection.objects.unlink(harvester_root)
    
    # 工业车体主壳
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.8))
    chassis = bpy.context.active_object
    chassis.scale = (4.4, 8.6, 2.2)
    chassis.parent = harvester_root
    chassis.data.materials.append(mats['HarvesterRed'])
    col_a.objects.link(chassis)
    scene.collection.objects.unlink(chassis)
    
    # 发动机侧舱百叶散热窗
    for side, sx in [('L', -2.25), ('R', 2.25)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(sx, -1.5, 2.0))
        grille = bpy.context.active_object
        grille.scale = (0.1, 3.2, 1.0)
        grille.parent = harvester_root
        grille.data.materials.append(mats['Treads'])
        col_a.objects.link(grille)
        scene.collection.objects.unlink(grille)
        
    # 双重型宽履带
    for side, x_off in [("L", -2.85), ("R", 2.85)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_off, 0, 1.2))
        tr = bpy.context.active_object
        tr.scale = (1.25, 9.2, 1.8)
        tr.parent = harvester_root
        tr.data.materials.append(mats['Treads'])
        col_a.objects.link(tr)
        scene.collection.objects.unlink(tr)
        
    # 封闭驾驶室与大曲面高透防暴玻璃
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 1.5, 3.6))
    cab = bpy.context.active_object
    cab.scale = (3.4, 3.4, 2.0)
    cab.parent = harvester_root
    cab.data.materials.append(mats['HarvesterRed'])
    col_a.objects.link(cab)
    scene.collection.objects.unlink(cab)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 3.22, 3.7))
    glass = bpy.context.active_object
    glass.scale = (3.1, 0.12, 1.4)
    glass.parent = harvester_root
    glass.data.materials.append(mats['GlassCyan'])
    col_a.objects.link(glass)
    scene.collection.objects.unlink(glass)
    
    # 前置重型旋转收割滚筒 + 侧向液压支撑臂
    for h_side, hx in [('L', -2.4), ('R', 2.4)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(hx, 3.2, 1.5))
        h_arm = bpy.context.active_object
        h_arm.scale = (0.25, 3.2, 0.35)
        h_arm.rotation_euler = (math.radians(-15), 0, 0)
        h_arm.parent = harvester_root
        h_arm.data.materials.append(mats['TurretOlive'])
        col_a.objects.link(h_arm)
        scene.collection.objects.unlink(h_arm)
        
    bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=4.8, location=(0, 4.8, 1.2))
    reel = bpy.context.active_object
    reel.rotation_euler = (0, math.radians(90), 0)
    reel.parent = harvester_root
    reel.data.materials.append(mats['MetalRust'])
    col_a.objects.link(reel)
    scene.collection.objects.unlink(reel)
    
    # 弯曲高耸柴油排气管 (曲面烟囱)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=2.8, location=(-1.8, -3.2, 3.8))
    exhaust = bpy.context.active_object
    exhaust.rotation_euler = (math.radians(12), 0, 0)
    exhaust.parent = harvester_root
    exhaust.data.materials.append(mats['SteelPolished'])
    col_a.objects.link(exhaust)
    scene.collection.objects.unlink(exhaust)
    
    # 车顶黄色警示旋转射灯
    for lx in [-1.3, 1.3]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.32, location=(lx, 3.1, 4.7))
        light = bpy.context.active_object
        light.rotation_euler = (math.radians(90), 0, 0)
        light.parent = harvester_root
        light.data.materials.append(mats['StatusYellow'])
        col_a.objects.link(light)
        scene.collection.objects.unlink(light)
    
    # 驾驶舱内坐姿人形假人：拉尔斯双手握方向盘，奥克塔维亚看仪表
    lars_driver = create_human_dummy("Lars_Driver", (-0.8, 1.5, 2.5), rot_deg=(0,0,0), scale=0.85, 
                                     suit_mat=mats['HumanSuitOrange'], skin_mat=mats['Skin'], parent=harvester_root, col=col_a)
    octavia_copilot = create_human_dummy("Octavia_Copilot", (0.8, 1.5, 2.5), rot_deg=(0,0,0), scale=0.80, 
                                         suit_mat=mats['HumanSuitBlue'], skin_mat=mats['Skin'], parent=harvester_root, col=col_a)
    
    # 驾驶舱控制台与双抓握方向盘 (Shot 03 特写)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.8, 2.3, 3.3))
    wheel_col = bpy.context.active_object
    wheel_col.scale = (0.1, 0.4, 0.1)
    wheel_col.rotation_euler = (math.radians(30), 0, 0)
    wheel_col.parent = harvester_root
    wheel_col.data.materials.append(mats['Treads'])
    col_a.objects.link(wheel_col)
    scene.collection.objects.unlink(wheel_col)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=0.28, minor_radius=0.04, location=(-0.8, 2.15, 3.45))
    steering_wheel = bpy.context.active_object
    steering_wheel.rotation_euler = (math.radians(60), 0, 0)
    steering_wheel.parent = harvester_root
    steering_wheel.data.materials.append(mats['Treads'])
    col_a.objects.link(steering_wheel)
    scene.collection.objects.unlink(steering_wheel)
    
    # 动画：收割机疾驰与滚筒旋转
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
    
    # 八角形防风阻隔堤坝 (带顶层走道)
    for i in range(8):
        ang = i * (2 * math.pi / 8)
        px = bx + math.cos(ang) * 38
        py = math.sin(ang) * 38
        bpy.ops.mesh.primitive_cube_add(size=1, location=(px, py, 2.0))
        wall = bpy.context.active_object
        wall.scale = (24, 4.5, 4.0)
        wall.rotation_euler = (0, 0, ang + math.pi/2)
        wall.data.materials.append(mats['RockDark'])
        col_b.objects.link(wall)
        scene.collection.objects.unlink(wall)
        
    # 双联装老式防空导弹塔
    tx, ty = bx - 6, 16
    bpy.ops.mesh.primitive_cylinder_add(radius=2.2, depth=6.8, location=(tx, ty, 3.4))
    pylon = bpy.context.active_object
    pylon.data.materials.append(mats['MetalRust'])
    col_b.objects.link(pylon)
    scene.collection.objects.unlink(pylon)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(tx, ty, 7.3))
    thead = bpy.context.active_object
    thead.scale = (3.8, 3.0, 1.8)
    thead.data.materials.append(mats['TurretOlive'])
    col_b.objects.link(thead)
    scene.collection.objects.unlink(thead)
    
    # 左右双联装 8 管导弹箱
    for side, off in [("L", -2.5), ("R", 2.5)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(tx + off, ty, 7.8))
        pod = bpy.context.active_object
        pod.scale = (1.6, 3.6, 2.0)
        pod.rotation_euler = (math.radians(-18), 0, 0)
        pod.data.materials.append(mats['TurretOlive'])
        col_b.objects.link(pod)
        scene.collection.objects.unlink(pod)
        
        # 弹箱前部 4 枚外露的导弹战斗部锥头
        for rx, rz in [(-0.4, -0.4), (0.4, -0.4), (-0.4, 0.4), (0.4, 0.4)]:
            bpy.ops.mesh.primitive_cone_add(radius1=0.18, radius2=0.0, depth=0.5, location=(tx + off + rx, ty + 1.8, 7.8 + rz))
            warhead = bpy.context.active_object
            warhead.rotation_euler = (math.radians(72), 0, 0)
            warhead.data.materials.append(mats['SteelPolished'])
            col_b.objects.link(warhead)
            scene.collection.objects.unlink(warhead)
        
    # 雷达抛物面天线与馈源桅杆
    bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=0.25, location=(tx, ty, 9.2))
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
    
    # 房间框架、地板、金属屋顶工字钢梁
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, 0, 2.2))
    room = bpy.context.active_object
    room.scale = (9.5, 7.5, 4.4)
    room.data.materials.append(mats['RockDark'])
    col_c.objects.link(room)
    scene.collection.objects.unlink(room)
    
    # 屋顶工字钢横梁
    for b_y in [-2.0, 0.0, 2.0]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, b_y, 4.2))
        beam = bpy.context.active_object
        beam.scale = (9.2, 0.35, 0.40)
        beam.data.materials.append(mats['TurretOlive'])
        col_c.objects.link(beam)
        scene.collection.objects.unlink(beam)
        
    # 重型金属工作台 (带桌下抽屉柜与侧边虎钳)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx + 2.5, 0, 0.95))
    bench = bpy.context.active_object
    bench.scale = (1.8, 4.6, 1.1)
    bench.data.materials.append(mats['MetalRust'])
    col_c.objects.link(bench)
    scene.collection.objects.unlink(bench)
    
    # 工作台上的工具：小型虎钳
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx + 2.4, 1.8, 1.6))
    vise = bpy.context.active_object
    vise.scale = (0.35, 0.40, 0.25)
    vise.data.materials.append(mats['SteelPolished'])
    col_c.objects.link(vise)
    scene.collection.objects.unlink(vise)
    
    # 工作台上的保温咖啡杯 (Shot 07 地震时滑落倒地动画)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.22, location=(cx + 2.4, 0.9, 1.6))
    mug = bpy.context.active_object
    mug.data.materials.append(mats['SteelPolished'])
    col_c.objects.link(mug)
    scene.collection.objects.unlink(mug)
    
    mug.rotation_euler = (0, 0, 0)
    mug.location = (cx + 2.4, 0.9, 1.6)
    mug.keyframe_insert(data_path="rotation_euler", frame=433)
    mug.keyframe_insert(data_path="location", frame=433)
    # 地震震翻
    mug.rotation_euler = (math.radians(90), 0, math.radians(35))
    mug.location = (cx + 2.3, 0.6, 1.55)
    mug.keyframe_insert(data_path="rotation_euler", frame=460)
    mug.keyframe_insert(data_path="location", frame=460)
    
    # 核心：影视级具象化地震记录仪！(Shot 06 大特写主角)
    seismo_root, stylus_pivot, paper_drum = create_realistic_seismograph(
        "Seismograph_Pro", (cx + 2.4, -0.4, 1.5), rot_deg=(0,0,0), scale=1.0, mats=mats, col=col_c
    )
    
    # 地震仪纸带滚筒匀速慢转动画 (Frame 361 to 432, Shot 06)
    paper_drum.rotation_euler = (math.radians(90), 0, 0)
    paper_drum.keyframe_insert(data_path="rotation_euler", frame=361)
    paper_drum.rotation_euler = (math.radians(90), math.radians(360), 0)
    paper_drum.keyframe_insert(data_path="rotation_euler", frame=432)
    
    # 地震仪检流计机械画笔在高频剧烈跳表动画 (Frame 361 to 432, Shot 06)
    for f in range(361, 433, 2):
        # 摆臂在纸带上左右狂摆，指针狠狠撞向极限刻度
        sw_z = math.sin(f * 0.9) * math.radians(26) + math.cos(f * 1.7) * math.radians(12)
        stylus_pivot.rotation_euler = (0, 0, sw_z)
        stylus_pivot.keyframe_insert(data_path="rotation_euler", frame=f)
        
    # 拉尔斯的手臂与手掌微距悬在仪器旋钮上方 (Shot 06 特写交代人机交互)
    lars_arm_close = create_human_dummy("Lars_CloseArm", (cx + 1.8, -0.4, 1.0), rot_deg=(0,0,90), scale=1.0,
                                        suit_mat=mats['HumanSuitOrange'], skin_mat=mats['Skin'], col=col_c)
    
    # 天花板晃动工业吊灯 (带保护网罩和金属长链条)
    bpy.ops.object.empty_add(type='ARROWS', location=(cx, -0.8, 4.3))
    lamp_pivot = bpy.context.active_object
    lamp_pivot.name = "Lamp_Pivot"
    col_c.objects.link(lamp_pivot)
    scene.collection.objects.unlink(lamp_pivot)
    
    # 悬挂金属链条
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1.6, location=(0, 0, -0.8))
    wire = bpy.context.active_object
    wire.parent = lamp_pivot
    wire.data.materials.append(mats['Treads'])
    col_c.objects.link(wire)
    scene.collection.objects.unlink(wire)
    
    # 锥形灯罩
    bpy.ops.mesh.primitive_cone_add(radius1=0.42, radius2=0.12, depth=0.35, location=(0, 0, -1.6))
    shade = bpy.context.active_object
    shade.parent = lamp_pivot
    shade.data.materials.append(mats['TurretOlive'])
    col_c.objects.link(shade)
    scene.collection.objects.unlink(shade)
    
    # 发光灯泡
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0, 0, -1.72))
    bulb = bpy.context.active_object
    bulb.parent = lamp_pivot
    bulb.data.materials.append(mats['WhiteLamp'])
    col_c.objects.link(bulb)
    scene.collection.objects.unlink(bulb)
    
    # 吊灯在地震镜头 (Frame 433 to 504, Shot 07) 狂甩动画
    for f in range(433, 505, 3):
        sw_x = math.sin(f * 0.42) * math.radians(34)
        sw_y = math.cos(f * 0.31) * math.radians(26)
        lamp_pivot.rotation_euler = (sw_x, sw_y, 0)
        lamp_pivot.keyframe_insert(data_path="rotation_euler", frame=f)
        
    # 防风百叶窗降下锁死动画 (Frame 289 to 360, Shot 05)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, 3.45, 4.0))
    shutter = bpy.context.active_object
    shutter.scale = (2.6, 0.14, 1.8)
    shutter.data.materials.append(mats['Treads'])
    col_c.objects.link(shutter)
    scene.collection.objects.unlink(shutter)
    
    shutter.location = (cx, 3.45, 3.9)
    shutter.keyframe_insert(data_path="location", frame=289)
    shutter.location = (cx, 3.45, 2.3)
    shutter.keyframe_insert(data_path="location", frame=332)
    
    # 板房内的人体假人 (拉尔斯在工作台前扶桌；奥克塔维亚在旁边抓住栏杆支撑)
    lars_inside = create_human_dummy("Lars_Inside", (cx + 1.2, -0.4, 0), rot_deg=(0,0,90), scale=0.95,
                                     suit_mat=mats['HumanSuitOrange'], skin_mat=mats['Skin'], col=col_c)
    octavia_inside = create_human_dummy("Octavia_Inside", (cx + 1.0, 0.8, 0), rot_deg=(0,0,105), scale=0.90,
                                       suit_mat=mats['HumanSuitBlue'], skin_mat=mats['Skin'], col=col_c)
    
    # 地震时人体身体失衡挣扎动画 (Frame 433 to 504)
    for f in range(433, 505, 3):
        lars_inside.rotation_euler = (math.sin(f*0.5)*math.radians(15), math.cos(f*0.3)*math.radians(8), math.radians(90))
        lars_inside.keyframe_insert(data_path="rotation_euler", frame=f)
        octavia_inside.rotation_euler = (math.cos(f*0.4)*math.radians(18), math.sin(f*0.5)*math.radians(10), math.radians(105))
        octavia_inside.keyframe_insert(data_path="rotation_euler", frame=f)

    # =========================================================================
    # SET E: 查尔星火山废土与刀锋女王王座 (X: 1300) -> Shot 08
    # =========================================================================
    col_e = bpy.data.collections.new("Set_E_PlanetChar")
    scene.collection.children.link(col_e)
    ex = 1300
    
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
        
    # 巨大的异虫螺旋尖塔 (Spire) 带几丁质肋骨
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=7.5, radius2=0.8, depth=65.0, location=(ex, 0, 32.5))
    main_spire = bpy.context.active_object
    main_spire.rotation_euler = (math.radians(6), math.radians(4), 0)
    main_spire.data.materials.append(mats['ZergPurple'])
    col_e.objects.link(main_spire)
    scene.collection.objects.unlink(main_spire)
    
    # 螺旋攀附的几丁质利角 (Chitinous Spikes)
    for sp_idx in range(6):
        ang = sp_idx * 1.1
        sz = 12.0 + sp_idx * 7.0
        sx = ex + math.cos(ang) * (6.0 - sp_idx * 0.7)
        sy = math.sin(ang) * (6.0 - sp_idx * 0.7)
        bpy.ops.mesh.primitive_cone_add(radius1=1.2, radius2=0.1, depth=5.5, location=(sx, sy, sz))
        horn = bpy.context.active_object
        horn.rotation_euler = (math.radians(35), math.radians(45), ang)
        horn.data.materials.append(mats['ZergBone'])
        col_e.objects.link(horn)
        scene.collection.objects.unlink(horn)
        
    # 异虫几丁质主巢王座平台
    bpy.ops.mesh.primitive_cylinder_add(radius=5.5, depth=1.8, location=(ex, 0, 48.0))
    throne_plat = bpy.context.active_object
    throne_plat.data.materials.append(mats['ZergBone'])
    col_e.objects.link(throne_plat)
    scene.collection.objects.unlink(throne_plat)
    
    # 刀锋女王凯瑞甘高空剪影假人（带标志性骨翼与骨刺发辫）
    kerrigan_dummy = create_human_dummy("Kerrigan_QueenOfBlades", (ex, 0, 48.9), rot_deg=(0,0,180), scale=1.4,
                                        suit_mat=mats['ZergPurple'], skin_mat=mats['ZergBone'], col=col_e)
    # 骨翼主刃与副刃 (Segmented Bone Wings)
    for wing_side, wx in [(-1.2, -1), (1.2, 1)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.25, 1.45))
        wing1 = bpy.context.active_object
        wing1.scale = (0.1, 1.6, 0.45)
        wing1.rotation_euler = (math.radians(35), math.radians(wx * 35), math.radians(wx * 20))
        wing1.parent = kerrigan_dummy
        wing1.data.materials.append(mats['ZergBone'])
        col_e.objects.link(wing1)
        scene.collection.objects.unlink(wing1)
        
        # 延伸尖端尖爪
        bpy.ops.mesh.primitive_cone_add(radius1=0.25, radius2=0.02, depth=1.8, location=(wx*1.2, -0.6, 1.8))
        talon = bpy.context.active_object
        talon.rotation_euler = (math.radians(50), math.radians(wx * 40), 0)
        talon.parent = kerrigan_dummy
        talon.data.materials.append(mats['ZergBone'])
        col_e.objects.link(talon)
        scene.collection.objects.unlink(talon)

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
    
    for side, y_off in [("North", -72), ("South", 72)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(dx, y_off, 45))
        cliff = bpy.context.active_object
        cliff.scale = (180, 50, 90)
        cliff.data.materials.append(mats['RockDark'])
        col_d.objects.link(cliff)
        scene.collection.objects.unlink(cliff)
        
    # 悬崖边缘对比比例尺道具：微型收割机与破碎栅栏
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
        
    # 顶部金字塔祭坛悬浮菱形核心晶体 (Shot 09, Shot 10 核心标志)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=6.5, radius2=0.0, depth=8.0, location=(dx, 0, 62.0))
    top_pyr = bpy.context.active_object
    top_pyr.rotation_euler = (0, 0, math.radians(45))
    top_pyr.data.materials.append(mats['XelNagaGlowBlue'])
    col_d.objects.link(top_pyr)
    scene.collection.objects.unlink(top_pyr)
    
    # 悬浮旋转动画
    top_pyr.rotation_euler = (0, 0, math.radians(45))
    top_pyr.keyframe_insert(data_path="rotation_euler", frame=577)
    top_pyr.rotation_euler = (0, 0, math.radians(405))
    top_pyr.keyframe_insert(data_path="rotation_euler", frame=792)
    
    # 神庙正门：巨型三角结晶门廊 (Shot 10 特写舞台)
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=8.5, depth=2.8, location=(dx, 42.5, 9.0))
    door = bpy.context.active_object
    door.rotation_euler = (math.radians(90), 0, 0)
    door.data.materials.append(mats['XelNagaGlowBlue'])
    col_d.objects.link(door)
    scene.collection.objects.unlink(door)
    
    # 门前拉尔斯具象化人体假人 (Shot 10 主角)
    lars_sh10 = create_human_dummy("Lars_TempleSacrifice", (dx, 40.0, 0.0), rot_deg=(0,0,0), scale=1.05,
                                   suit_mat=mats['HumanSuitOrange'], skin_mat=mats['Skin'], col=col_d)
    
    # 动画：拉尔斯走向大门 -> 引力悬浮升空 -> 强光中粒子瓦解消散
    lars_sh10.location = (dx, 38.0, 0.0)
    lars_sh10.keyframe_insert(data_path="location", frame=673)
    lars_sh10.location = (dx, 41.2, 0.0)
    lars_sh10.keyframe_insert(data_path="location", frame=705)
    
    lars_sh10.location = (dx, 41.2, 4.8)
    lars_sh10.keyframe_insert(data_path="location", frame=730)
    
    lars_sh10.scale = (1.05, 1.05, 1.05)
    lars_sh10.keyframe_insert(data_path="scale", frame=730)
    lars_sh10.scale = (0.001, 0.001, 0.001)
    lars_sh10.keyframe_insert(data_path="scale", frame=742)
    
    # 24 颗向外扩散的高能粒子群 (身体瓦解视觉化)
    for p_i in range(24):
        ang = p_i * (2 * math.pi / 24)
        elev = (p_i % 3 - 1) * 0.4
        px = dx + math.cos(ang) * 0.4
        py = 41.2 + math.sin(ang) * 0.4
        pz = 4.8 + elev
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(px, py, pz))
        pt = bpy.context.active_object
        pt.data.materials.append(mats['XelNagaGlowBlue'])
        col_d.objects.link(pt)
        scene.collection.objects.unlink(pt)
        
        pt.scale = (0.001, 0.001, 0.001)
        pt.keyframe_insert(data_path="scale", frame=725)
        pt.scale = (1.8, 1.8, 1.8)
        pt.keyframe_insert(data_path="scale", frame=738)
        pt.location = (dx + math.cos(ang) * 6.5, 41.2 + math.sin(ang) * 3.5, 4.8 + elev * 4.0)
        pt.keyframe_insert(data_path="location", frame=748)
        pt.scale = (0.001, 0.001, 0.001)
        pt.keyframe_insert(data_path="scale", frame=752)
        
    # 450米宇宙纯能信标光柱 (自神庙顶端轰然冲上云霄)
    bpy.ops.mesh.primitive_cylinder_add(radius=5.8, depth=450.0, location=(dx, 0, -250))
    beam = bpy.context.active_object
    beam.data.materials.append(mats['BeaconBeam'])
    col_d.objects.link(beam)
    scene.collection.objects.unlink(beam)
    
    beam.location = (dx, 0, -250)
    beam.keyframe_insert(data_path="location", frame=735)
    beam.location = (dx, 0, 275)
    beam.keyframe_insert(data_path="location", frame=755)
    
    # 双螺旋旋转能量护鞘环 (Dual Helical Rings)
    bpy.ops.mesh.primitive_cylinder_add(radius=7.5, depth=420.0, location=(dx, 0, 275))
    sheath = bpy.context.active_object
    sheath.data.materials.append(mats['XelNagaGlowBlue'])
    col_d.objects.link(sheath)
    scene.collection.objects.unlink(sheath)
    
    sheath.scale = (0.001, 0.001, 0.001)
    sheath.keyframe_insert(data_path="scale", frame=740)
    sheath.scale = (1.0, 1.0, 1.0)
    sheath.keyframe_insert(data_path="scale", frame=760)
    
    # 4重大气层激波扩散环
    for r_idx, (r_rad, r_z) in enumerate([(35.0, 140.0), (70.0, 230.0), (110.0, 320.0), (160.0, 420.0)]):
        bpy.ops.mesh.primitive_torus_add(major_radius=r_rad, minor_radius=2.5, location=(dx, 0, r_z))
        ring = bpy.context.active_object
        ring.data.materials.append(mats['BeaconBeam'])
        col_d.objects.link(ring)
        scene.collection.objects.unlink(ring)
        
        ring.scale = (0.01, 0.01, 0.01)
        ring.keyframe_insert(data_path="scale", frame=740 + r_idx * 12)
        ring.scale = (2.4, 2.4, 2.4)
        ring.keyframe_insert(data_path="scale", frame=775 + r_idx * 12)

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
    
    # 6. Shot 06 (Frame 361-432): 地震仪真实仪器与纸带跳表长焦特写 (85mm 微距)
    # 机位：正侧微俯视紧贴纸带滚筒与跳针，画面清晰展现滚筒网格、机械摆臂与红墨尖头剧烈跳动！
    cam09 = create_cam("Cam_09_SeismographECU", (502.8, -0.4, 2.22), (84, 0, -90), lens=85.0)
    for f in range(361, 433, 4):
        cam09.location = (502.8 + (f%3-1)*0.012, -0.4 + (f%2-1)*0.012, 2.22)
        cam09.keyframe_insert(data_path="location", frame=f)
    bind_marker("Shot06_SeismographECU", 361, cam09)
    
    # 7. Shot 07 (Frame 433-504): 大地震剧烈晃动，吊灯狂摆、保温杯翻倒与警报 (35mm)
    cam10 = create_cam("Cam_10_HomesteadQuake", (498.2, 0.4, 2.3), (85, 0, 70), lens=35.0)
    for f in range(433, 505, 2):
        q = (f % 5 - 2) * 0.15
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

# 镜头导演解说字幕数据库
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
        "title": "SHOT 06 / 10 | 兄妹工作台 · 简易地震仪走纸滚筒与指针跳表特写",
        "lens": "85mm 长焦微距 | 地震仪走纸滚筒、机械悬臂与红墨尖头",
        "action": "【剧情调度】原本平稳的图纸滚筒匀速转动，机械画笔指针突然剧烈狂摆打到爆表，地底深处震动！",
        "intent": "【视听意图】未知危机的第一个信号，精密机械仪器的失控撬动整个星球维度的宏大灾变悬念。"
    },
    (433, 504): {
        "title": "SHOT 07 / 10 | 板房大地震 · 吊灯狂甩、保温杯翻倒与红光警报",
        "lens": "35mm 剧烈手持晃动 | 8.5级罕见大地震爆发",
        "action": "【剧情调度】大地震爆发！房顶吊灯疯狂甩荡，工作台器械与保温杯翻倒，应急红灯狂闪，兄妹两人死死抓牢桌沿支撑。",
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
    使用 PIL + OpenCV 为每一帧添加电影级导演监视器 HUD 与解说字幕
    """
    frame_files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.png")))
    total_frames = len(frame_files)
    if total_frames == 0:
        raise RuntimeError(f"No frames found in {frames_dir} to compile video!")
        
    print(f"[Platform/Blender] Compiling {total_frames} frames with Director HUD into: {output_mp4} ...")
    
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
            
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb).convert('RGBA')
        
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # 1. 顶部时间码栏 (Top Bar)
        draw.rectangle([(0, 0), (width, 42)], fill=(15, 18, 22, 215))
        sec = int(frame_num / fps)
        rem_f = int(frame_num % fps)
        tc_str = f"TC 00:00:{sec:02d}:{rem_f:02d} | FRAME {frame_num:03d}/{total_frames} | 24 FPS"
        draw.text((35, 8), tc_str, font=font_tc, fill=(160, 210, 255, 255))
        draw.text((width - 450, 8), "STARCRAFT: SHADOW OF THE XEL'NAGA - PREVIS", font=font_tc, fill=(200, 200, 200, 220))
        
        # 2. 底部电影级解说字幕条 (Bottom Director HUD)
        cap = get_caption_for_frame(frame_num)
        if cap:
            hud_h = 135
            draw.rectangle([(0, height - hud_h), (width, height)], fill=(12, 14, 18, 228))
            draw.line([(0, height - hud_h), (width, height - hud_h)], fill=(255, 195, 0, 190), width=2)
            
            draw.text((45, height - 124), f"🎬 {cap['title']}", font=font_title, fill=(255, 215, 0, 255))
            draw.text((width - 420, height - 120), cap['lens'], font=font_sub, fill=(130, 200, 255, 240))
            draw.text((45, height - 82), cap['action'], font=font_sub, fill=(245, 245, 245, 255))
            draw.text((45, height - 48), cap['intent'], font=font_sub, fill=(175, 185, 195, 240))
            
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
    print(f"[Platform/Blender] SUCCESS: Saved realistic work .blend to {work_blend}")
    
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

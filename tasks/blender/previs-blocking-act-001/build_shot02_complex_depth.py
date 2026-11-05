"""
build_shot02_complex_depth.py
升级 Shot 02 动态超车复杂深度与预演工程 (5.0s, 120帧, 768x320 2.4:1)
包含：载具层次丰富化（负重轮、液压臂、旋转切割滚刀）、极强近景路桩视差、垄沟地形流与镜头超车透视流转。
"""

import bpy
import math
import os

def create_complex_shot02_from_base():
    base_blend = r'D:\nano-video-studio\tasks\blender\previs-blocking-act-001\work\previs_act01_video.blend'
    out_blend = r'D:\nano-video-studio\tasks\blender\previs-blocking-act-001\work\previs_act01_shot02_complex_depth.blend'
    
    bpy.ops.wm.open_mainfile(filepath=base_blend)
    scene = bpy.context.scene

    # 1. Output Settings: 768x320, 120 frames (5.0s @ 24fps)
    scene.render.resolution_x = 768
    scene.render.resolution_y = 320
    scene.render.resolution_percentage = 100
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 120

    # Clean up markers and unused collections
    scene.timeline_markers.clear()
    for col in list(scene.collection.children):
        if col.name not in ['Set_A_BhekarRo_Plains', 'Cameras_Animatic']:
            scene.collection.children.unlink(col)

    # Clean up other cameras except Cam_02_HarvesterTrack
    cam02 = bpy.data.objects.get('Cam_02_HarvesterTrack')
    for o in list(bpy.data.objects):
        if o.type == 'CAMERA' and o != cam02:
            bpy.data.objects.remove(o)

    scene.camera = cam02
    cam02.name = "Cam_02_DynamicOvertake"
    cam02.data.lens = 32.0  # 32mm cinematic lens
    cam02.data.clip_start = 0.5
    cam02.data.clip_end = 250.0

    col_a = bpy.data.collections.get('Set_A_BhekarRo_Plains')
    mats = bpy.data.materials
    mat_metal = mats.get('Treads')
    mat_red = mats.get('HarvesterRed')
    
    def get_or_make_mat(name, color, roughness=0.5, metallic=0.0):
        m = bpy.data.materials.get(name)
        if not m:
            m = bpy.data.materials.new(name=name)
            nodes = m.node_tree.nodes
            nodes.clear()
            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            bsdf.inputs['Base Color'].default_value = color
            bsdf.inputs['Roughness'].default_value = roughness
            bsdf.inputs['Metallic'].default_value = metallic
            out = nodes.new(type='ShaderNodeOutputMaterial')
            m.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        return m

    mat_post = get_or_make_mat("Mat_HazardPost", (0.7, 0.55, 0.1, 1.0), roughness=0.5, metallic=0.3)
    mat_ref = get_or_make_mat("Mat_HazardReflector", (0.9, 0.1, 0.1, 1.0), roughness=0.2, metallic=0.0)
    mat_furrow = get_or_make_mat("Mat_WheatRidge", (0.38, 0.28, 0.16, 1.0), roughness=0.9, metallic=0.0)

    # 2. Enrich Harvester details
    harv_root = bpy.data.objects.get('Harvester_Root')
    if harv_root.animation_data:
        harv_root.animation_data_clear()

    # Find cutter reel in children
    reel = None
    for c in harv_root.children:
        if 'Cylinder' in c.name and c.dimensions.y > 4.0:
            reel = c
            reel.name = "Cutter_Reel"
            break

    # Add 12 Road Wheels under tracks (6 on Left, 6 on Right)
    all_wheels = []
    for side, tx in [('L', -2.85), ('R', 2.85)]:
        for wy in [-3.5, -2.1, -0.7, 0.7, 2.1, 3.5]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.52, depth=0.6, location=(tx, wy, 0.6))
            wheel = bpy.context.active_object
            wheel.name = f"Wheel_{side}_{wy}"
            wheel.rotation_euler = (0, math.radians(90), 0)
            wheel.parent = harv_root
            if mat_metal:
                wheel.data.materials.append(mat_metal)
            col_a.objects.link(wheel)
            scene.collection.objects.unlink(wheel)
            all_wheels.append(wheel)

    # Add hydraulic boom arms on left and right for front cutter
    for side, bx in [('L', -2.5), ('R', 2.5)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, 3.0, 1.4))
        boom = bpy.context.active_object
        boom.name = f"Hydraulic_Boom_{side}"
        boom.scale = (0.3, 2.8, 0.4)
        boom.rotation_euler = (math.radians(-20), 0, 0)
        boom.parent = harv_root
        if mat_red:
            boom.data.materials.append(mat_red)
        col_a.objects.link(boom)
        scene.collection.objects.unlink(boom)

    # 3. Enrich Environment: Furrows & Foreground Hazard Boundary Posts
    for rx in [-15, -12, -9, 6, 9, 12, 15, 18]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(rx, 0, 0.12))
        ridge = bpy.context.active_object
        ridge.name = f"Wheat_Ridge_{rx}"
        ridge.scale = (1.4, 250, 0.22)
        ridge.data.materials.append(mat_furrow)
        col_a.objects.link(ridge)
        scene.collection.objects.unlink(ridge)

    # Foreground Hazard Boundary Posts along X = -7.0 (between camera at X = -15.0 and vehicle at X = 0.0)
    for py in range(-45, 55, 7):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=1.7, location=(-7.0, py, 0.85))
        post = bpy.context.active_object
        post.name = f"Hazard_Post_{py}"
        post.data.materials.append(mat_post)
        col_a.objects.link(post)
        scene.collection.objects.unlink(post)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.25, location=(-7.0, py, 1.6))
        ref = bpy.context.active_object
        ref.name = f"Hazard_Reflector_{py}"
        ref.parent = post
        ref.data.materials.append(mat_ref)
        col_a.objects.link(ref)
        scene.collection.objects.unlink(ref)

    # 4. Animation: Harvester Moves 60m along -Y over 120 frames
    harv_root.location = (0, 38.0, 0)
    harv_root.keyframe_insert(data_path="location", frame=1)
    harv_root.location = (0, -22.0, 0)
    harv_root.keyframe_insert(data_path="location", frame=120)

    # Cutter reel spinning
    if reel:
        reel.rotation_euler = (0, math.radians(90), 0)
        reel.keyframe_insert(data_path="rotation_euler", frame=1)
        reel.rotation_euler = (math.radians(-4320), math.radians(90), 0)
        reel.keyframe_insert(data_path="rotation_euler", frame=120)

    # Wheels rolling along ground
    for wheel in all_wheels:
        wheel.rotation_euler = (0, math.radians(90), 0)
        wheel.keyframe_insert(data_path="rotation_euler", frame=1)
        wheel.rotation_euler = (math.radians(-6264), math.radians(90), 0)
        wheel.keyframe_insert(data_path="rotation_euler", frame=120)

    # 5. Dynamic Camera Animation: Overtaking Low-Angle Tracking Shot
    if cam02.animation_data:
        cam02.animation_data_clear()

    def point_cam(camera, target):
        import mathutils
        dir_vec = mathutils.Vector(target) - camera.location
        camera.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()

    for f in range(1, 121):
        t = (f - 1) / 119.0
        # Cam Y starts at 46.0 (8m behind harvester) and overtakes to -30.0 (8m ahead of harvester)
        cam_y = 46.0 + t * (-30.0 - 46.0)
        # Cam X stays at ~15m distance with subtle arc
        cam_x = -14.5 - math.sin(t * math.pi) * 1.5
        jitter_z = math.sin(f * 2.2) * 0.02 + math.cos(f * 3.5) * 0.01
        cam_z = 3.8 + t * (2.6 - 3.8) + jitter_z
        cam02.location = (cam_x, cam_y, cam_z)

        # Target moves along with vehicle from rear-quarter to front-center, offset +2.5 in X to hold left 50%
        harv_y = 38.0 + t * (-22.0 - 38.0)
        target_y = harv_y + (1.0 - t * 3.0)
        target_x = 2.5
        target_z = 2.0 - t * 0.4
        point_cam(cam02, (target_x, target_y, target_z))

        if f in [1, 15, 30, 45, 60, 75, 90, 105, 120] or f % 3 == 0:
            cam02.keyframe_insert(data_path="location", frame=f)
            cam02.keyframe_insert(data_path="rotation_euler", frame=f)

    # 6. Compositor Node Setup for True Depth in Blender 5.2
    scene.view_layers[0].use_pass_z = True
    ng = bpy.data.node_groups.new("Compositor Nodes", "CompositorNodeTree")
    scene.compositing_node_group = ng
    ng.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    rl = ng.nodes.new("CompositorNodeRLayers")
    rl.location = (-400, 200)

    # Map Range: 6.0m to 36.0m mapped to 1.0 -> 0.0
    map_range = ng.nodes.new("ShaderNodeMapRange")
    map_range.name = "Map Range"
    map_range.location = (-150, 200)
    map_range.inputs['From Min'].default_value = 6.0
    map_range.inputs['From Max'].default_value = 36.0
    map_range.inputs['To Min'].default_value = 1.0
    map_range.inputs['To Max'].default_value = 0.0

    g_out = ng.nodes.new("NodeGroupOutput")
    g_out.name = "Group Output"
    g_out.location = (350, 200)

    ng.links.new(rl.outputs['Depth'], map_range.inputs['Value'])
    ng.links.new(map_range.outputs['Result'], g_out.inputs['Image'])

    os.makedirs(os.path.dirname(out_blend), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print("SUCCESSFULLY_BUILT_COMPLEX_SHOT02:", out_blend)

if __name__ == '__main__':
    create_complex_shot02_from_base()

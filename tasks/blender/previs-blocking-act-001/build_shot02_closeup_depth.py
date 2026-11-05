import bpy
import math
import os

# 1. Base blend
base_blend = r"D:\nano-video-studio\tasks\blender\previs-blocking-act-001\work\previs_act01_video.blend"
bpy.ops.wm.open_mainfile(filepath=base_blend)

scene = bpy.context.scene
scene.render.resolution_x = 768
scene.render.resolution_y = 320
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 124

# Clear existing timeline markers to avoid camera auto-switching
scene.timeline_markers.clear()

root = scene.objects.get("Harvester_Root")
if not root:
    raise RuntimeError("Harvester_Root not found")

# Create or reuse dynamic close-up camera
cam_name = "Cam_02_CloseupDynamic"
if cam_name in scene.objects:
    cam = scene.objects[cam_name]
else:
    cam_data = bpy.data.cameras.new(cam_name)
    cam = bpy.data.objects.new(cam_name, cam_data)
    scene.collection.objects.link(cam)

cam.data.lens = 35.0
cam.data.sensor_width = 36.0
cam.data.sensor_height = 24.0
cam.data.clip_start = 0.1
cam.data.clip_end = 500.0
scene.camera = cam

# Set up Harvester_Root animation for 124 frames (5.17s)
# Moving smoothly from Y = 38.0 to Y = -24.0
root.animation_data_clear()
root.location = (0.0, 38.0, 0.0)
root.keyframe_insert(data_path="location", frame=1)
root.location = (0.0, -24.0, 0.0)
root.keyframe_insert(data_path="location", frame=124)

# Linear interpolation for harvester motion
if root.animation_data and root.animation_data.action:
    # Set all fcurve keyframes to linear
    act = root.animation_data.action
    # In Blender 5.x, try fcurves or iterate
    try:
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'
    except Exception:
        pass

# Set up Camera motion (Dynamic Close-up Tracking & Smooth Overtake)
cam.animation_data_clear()

# Keyframe 1: Exact close-up side-rear tracking (Shot 02 origin)
# Root is at Y = 38.0. Cam is at (-10.5, 43.5, 3.8) -> delta Y = +5.5m behind cabin
cam.location = (-10.5, 43.5, 3.8)
cam.rotation_euler = (math.radians(80.4), 0.0, math.radians(-126.03))
cam.keyframe_insert(data_path="location", frame=1)
cam.keyframe_insert(data_path="rotation_euler", frame=1)

# Keyframe 40: Alongside rear cabin & exhaust
# Root Y = 38 - (40-1)/123 * 62 = 38 - 19.67 = 18.33
# Cam delta Y = +3.0m behind root
cam.location = (-10.0, 18.33 + 3.0, 3.6)
cam.rotation_euler = (math.radians(81.0), 0.0, math.radians(-123.0))
cam.keyframe_insert(data_path="location", frame=40)
cam.keyframe_insert(data_path="rotation_euler", frame=40)

# Keyframe 85: Sliding past mid-cabin towards front tracks
# Root Y = 38 - (85-1)/123 * 62 = 38 - 42.34 = -4.34
# Cam delta Y = 0.0m (level with cabin center)
cam.location = (-9.6, -4.34 + 0.0, 3.4)
cam.rotation_euler = (math.radians(81.5), 0.0, math.radians(-118.0))
cam.keyframe_insert(data_path="location", frame=85)
cam.keyframe_insert(data_path="rotation_euler", frame=85)

# Keyframe 124: Smooth overtake, viewing side-front cutter reel
# Root Y = -24.0
# Cam delta Y = -3.5m ahead of cabin center, panning back slightly to keep reel & cabin in 3/4
cam.location = (-9.2, -24.0 - 3.5, 3.2)
cam.rotation_euler = (math.radians(82.0), 0.0, math.radians(-112.0))
cam.keyframe_insert(data_path="location", frame=124)
cam.keyframe_insert(data_path="rotation_euler", frame=124)

# Set interpolation to bezier for smooth camera acceleration
try:
    if cam.animation_data and cam.animation_data.action:
        for fc in cam.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
except Exception:
    pass

# Ensure ViewLayer has Z Depth enabled
vl = scene.view_layers["ViewLayer"]
vl.use_pass_z = True

# Enable compositor node tree
scene.use_nodes = True
tree = getattr(scene, 'node_tree', None)
if tree is None and hasattr(scene, 'compositing_node_group'):
    tree = scene.compositing_node_group
if tree is None:
    # Look in bpy.data.node_groups
    for ng in bpy.data.node_groups:
        if ng.type == 'COMPOSITING':
            tree = ng
            break

if tree is None:
    tree = bpy.data.node_groups.new("Compositor Nodes", "CompositorNodeTree")
    scene.compositing_node_group = tree

tree.nodes.clear()
rl = tree.nodes.new("CompositorNodeRLayers")
rl.location = (0, 0)

# Map Range: calibrated 4.0m to 22.0m for extreme contrast
map_node = tree.nodes.new("ShaderNodeMapRange")
map_node.location = (250, 0)
map_node.inputs['From Min'].default_value = 4.0
map_node.inputs['From Max'].default_value = 22.0
map_node.inputs['To Min'].default_value = 1.0
map_node.inputs['To Max'].default_value = 0.0
map_node.clamp = True

# ColorRamp for S-curve edge contrast enhancement
ramp_node = tree.nodes.new("ShaderNodeValToRGB")
ramp_node.location = (450, 0)
ramp_node.color_ramp.elements[0].position = 0.10
ramp_node.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
ramp_node.color_ramp.elements[1].position = 0.85
ramp_node.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)

out_node = tree.nodes.new("NodeGroupOutput")
out_node.location = (700, 0)

# Link Z to Map Range -> ColorRamp -> Group Output
tree.links.new(rl.outputs['Depth'], map_node.inputs['Value'])
tree.links.new(map_node.outputs['Result'], ramp_node.inputs['Fac'])
tree.links.new(ramp_node.outputs['Color'], out_node.inputs[0])

# Save blend file
save_blend = r"D:\nano-video-studio\tasks\blender\previs-blocking-act-001\work\previs_act01_shot02_closeup_depth.blend"
bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print("Saved blend file:", save_blend)

# Test render frame 1
scene.frame_set(1)
scene.render.filepath = r"D:\nano-video-studio\tasks\video-act01-shot02-reference-test\test_closeup_depth_f001.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_closeup_depth_f001.png")

# Test render frame 60
scene.frame_set(60)
scene.render.filepath = r"D:\nano-video-studio\tasks\video-act01-shot02-reference-test\test_closeup_depth_f060.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_closeup_depth_f060.png")

# Test render frame 124
scene.frame_set(124)
scene.render.filepath = r"D:\nano-video-studio\tasks\video-act01-shot02-reference-test\test_closeup_depth_f124.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_closeup_depth_f124.png")

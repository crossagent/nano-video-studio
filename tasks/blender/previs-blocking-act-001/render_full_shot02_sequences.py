import bpy
import math
import os

blend_path = r"D:\nano-video-studio\tasks\blender\previs-blocking-act-001\work\previs_act01_shot02_true_depth.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)

scene = bpy.context.scene
scene.render.resolution_x = 768
scene.render.resolution_y = 320
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 124
scene.render.image_settings.media_type = 'IMAGE'
scene.render.image_settings.file_format = 'PNG'

# Clear markers
scene.timeline_markers.clear()

root = scene.objects["Harvester_Root"]
cam = scene.objects["Cam_02_HarvesterTrack"]
scene.camera = cam

# Set up Harvester_Root animation: 76m travel over 124 frames
root.animation_data_clear()
root.location = (0.0, 38.0, 0.0)
root.keyframe_insert(data_path="location", frame=1)
root.location = (0.0, -38.0, 0.0)
root.keyframe_insert(data_path="location", frame=124)

try:
    if root.animation_data and root.animation_data.action:
        for fc in root.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'
except Exception:
    pass

# Dynamic Camera Animation (Close-up Side-Rear to Front-Flank Overtake)
cam.animation_data_clear()

# Frame 1: Original Shot 02 close-up side-rear tracking
cam.location = (-11.0, 44.0, 4.5)
cam.rotation_euler = (math.radians(80.4), 0.0, math.radians(-126.03))
cam.keyframe_insert(data_path="location", frame=1)
cam.keyframe_insert(data_path="rotation_euler", frame=1)

# Frame 45: Gliding past cabin
cam.location = (-10.5, 10.81 + 3.5, 4.1)
cam.rotation_euler = (math.radians(80.8), 0.0, math.radians(-123.0))
cam.keyframe_insert(data_path="location", frame=45)
cam.keyframe_insert(data_path="rotation_euler", frame=45)

# Frame 85: Level with cabin & forward chassis
cam.location = (-10.0, -13.92 + 0.5, 3.7)
cam.rotation_euler = (math.radians(81.2), 0.0, math.radians(-119.0))
cam.keyframe_insert(data_path="location", frame=85)
cam.keyframe_insert(data_path="rotation_euler", frame=85)

# Frame 124: Smooth overtake past front cutter
cam.location = (-9.5, -38.0 - 3.0, 3.3)
cam.rotation_euler = (math.radians(81.8), 0.0, math.radians(-114.0))
cam.keyframe_insert(data_path="location", frame=124)
cam.keyframe_insert(data_path="rotation_euler", frame=124)

try:
    if cam.animation_data and cam.animation_data.action:
        for fc in cam.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
except Exception:
    pass

# Ensure ViewLayer pass_z is True
vl = scene.view_layers["ViewLayer"]
vl.use_pass_z = True

# Compositor Tree
tree = bpy.data.node_groups['Compositor Nodes']
tree.nodes.clear()

rl = tree.nodes.new("CompositorNodeRLayers")
rl.location = (0, 0)

map_node = tree.nodes.new("ShaderNodeMapRange")
map_node.location = (250, 0)
map_node.inputs['From Min'].default_value = 0.0
map_node.inputs['From Max'].default_value = 25.0
map_node.inputs['To Min'].default_value = 1.0
map_node.inputs['To Max'].default_value = 0.0
map_node.clamp = True

out_node = tree.nodes.new("NodeGroupOutput")
out_node.location = (500, 0)

# Save blend
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print("Updated blend saved.")

depth_dir = r"D:\nano-video-studio\tasks\comfyui\video-act01-shot02-reference-test\depth_frames"
previs_dir = r"D:\nano-video-studio\tasks\comfyui\video-act01-shot02-reference-test\previs_frames"
os.makedirs(depth_dir, exist_ok=True)
os.makedirs(previs_dir, exist_ok=True)

# 1. Render Depth frames
print("Rendering 124 Depth frames...")
tree.links.clear()
tree.links.new(rl.outputs['Depth'], map_node.inputs['Value'])
tree.links.new(map_node.outputs['Result'], out_node.inputs[0])

for f in range(1, 125):
    scene.frame_set(f)
    scene.render.filepath = os.path.join(depth_dir, f"frame_{f:04d}.png")
    bpy.ops.render.render(write_still=True)
    if f % 25 == 0 or f == 1 or f == 124:
        print(f"  Depth frame {f}/124 rendered")

# 2. Render RGB Previs frames
print("Rendering 124 RGB Previs frames...")
tree.links.clear()
tree.links.new(rl.outputs['Image'], out_node.inputs[0])

for f in range(1, 125):
    scene.frame_set(f)
    scene.render.filepath = os.path.join(previs_dir, f"frame_{f:04d}.png")
    bpy.ops.render.render(write_still=True)
    if f % 25 == 0 or f == 1 or f == 124:
        print(f"  RGB frame {f}/124 rendered")

print("All frames rendered successfully.")

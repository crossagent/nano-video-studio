import bpy
import os

blend_path = r"D:\nano-video-studio\tasks\blender\previs-blocking-act-001\work\previs_act01_shot02_true_depth.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.render.resolution_x = 768
scene.render.resolution_y = 320
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.render.image_settings.media_type = 'IMAGE'
scene.render.image_settings.file_format = 'PNG'

# In workbench, disable compositing node tree or route Image directly
tree = getattr(scene, 'compositing_node_group', None)
if tree:
    out = [n for n in tree.nodes if n.type == 'GROUP_OUTPUT'][0]
    rl = [n for n in tree.nodes if n.type == 'R_LAYERS'][0]
    tree.links.clear()
    tree.links.new(rl.outputs['Image'], out.inputs[0])

previs_dir = r"D:\nano-video-studio\tasks\comfyui\video-act01-shot02-reference-test\previs_frames"
os.makedirs(previs_dir, exist_ok=True)

print("Rendering 124 RGB Previs frames with Workbench...")
for f in range(1, 125):
    scene.frame_set(f)
    scene.render.filepath = os.path.join(previs_dir, f"frame_{f:04d}.png")
    bpy.ops.render.render(write_still=True)
    if f % 30 == 0 or f == 1 or f == 124:
        print(f"  RGB frame {f}/124 rendered")

print("Done rendering RGB previs frames.")

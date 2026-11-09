import bpy, math
from mathutils import Vector
from pathlib import Path

root = Path(r'D:\nano-video-studio\tasks\blender\act01-shared-world')
scene = bpy.context.scene
cam = bpy.data.objects['Cam_03_CockpitMS']
action = cam.animation_data.action
try:
    curves = action.fcurves
except AttributeError:
    curves = action.layers[0].strips[0].channelbag(cam.animation_data.action_slot).fcurves
for curve in curves:
    if curve.data_path != 'rotation_euler' or curve.array_index != 2:
        continue
    last = None
    for key in curve.keyframe_points:
        val = key.co.y
        if last is not None:
            val += round((last - val) / (2 * math.pi)) * 2 * math.pi
        delta = val - key.co.y
        key.co.y += delta
        key.handle_left.y += delta
        key.handle_right.y += delta
        last = val
    curve.update()

# Place the existing character on the forward edge of the shared throne,
# outside the solid central spire, facing the camera.
queen = bpy.data.objects['Kerrigan_QueenOfBlades']
queen.location.y = 4.0
queen.rotation_euler.z = 0
# Move the two coarse wing plates away from the face in the frontal view.
for name, side in [('Cube.068', -1), ('Cube.069', 1)]:
    wing = bpy.data.objects[name]
    wing.location = (side * 0.8, -0.25, 1.65)
    wing.rotation_euler = (0, side * math.radians(28), 0)
    wing.scale = (0.12, 0.16, 1.5)
cam = bpy.data.objects['Cam_12_CharHive']
cam.animation_data_clear()
cam.rotation_mode = 'XYZ'
cam.data.lens = 35
last_euler = None
for frame, pos in [(505, (1300, 17.5, 52.0)), (576, (1300, 11.5, 51.6))]:
    cam.location = pos
    q = (Vector((1300, 4, 50.5)) - cam.location).to_track_quat('-Z', 'Y')
    cam.rotation_euler = q.to_euler('XYZ', last_euler) if last_euler else q.to_euler('XYZ')
    last_euler = cam.rotation_euler.copy()
    cam.keyframe_insert(data_path='location', frame=frame)
    cam.keyframe_insert(data_path='rotation_euler', frame=frame)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(root / 'work' / 'act01_shared_world_camera_fix.blend'))
scene.render.resolution_percentage = 50
scene.render.image_settings.file_format = 'PNG'
for frame in [145, 148, 149, 150, 151, 154, 155, 156, 157, 505, 525, 545, 576]:
    scene.frame_set(frame)
    scene.render.filepath = str(root / 'output' / 'checks' / f'camera_fix_{frame:04d}.png')
    bpy.ops.render.render(write_still=True)
    print('FIX_CHECK', frame, flush=True)

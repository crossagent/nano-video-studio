import bpy
from pathlib import Path
root = Path(r'D:\nano-video-studio\tasks\blender\act01-shared-world')
frames = root / 'work' / 'frames_camera_fix'
frames.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(frames / 'frame_')
scene.frame_start = 1
scene.frame_end = 792
bpy.ops.render.render(animation=True)
print('CAMERA_FIX_RENDER_COMPLETE', flush=True)

import bpy
from pathlib import Path

root = Path(r'D:\nano-video-studio\tasks\blender\act01-shared-world')
s = bpy.context.scene
s.render.resolution_x = 1920
s.render.resolution_y = 804
s.render.resolution_percentage = 100
s.render.fps = 24
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGB'
frames = root / 'work' / 'frames'
frames.mkdir(parents=True, exist_ok=True)
s.render.filepath = str(frames / 'frame_')
print('RENDER_BEGIN', s.frame_start, s.frame_end, s.render.filepath, flush=True)
bpy.ops.render.render(animation=True)
print('RENDER_COMPLETE', flush=True)

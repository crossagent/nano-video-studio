from pathlib import Path

import bpy


scene = bpy.context.scene
output = Path(__file__).resolve().parent / 'work' / 'canyon_frames'
output.mkdir(exist_ok=True)
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.compression = 15
scene.render.filepath = str(output / 'canyon-')
bpy.ops.render.render(animation=True)

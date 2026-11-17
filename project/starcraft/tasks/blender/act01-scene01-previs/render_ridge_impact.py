from pathlib import Path

import bpy


scene = bpy.context.scene
bolt = bpy.data.objects['FX_S01_Lightning_Core']
rock = bpy.data.objects['FX_S01_Intact_Outcrop']
fragment = bpy.data.objects['FX_S01_Ridge_Fragment_00']
scene.frame_set(196)
assert not rock.hide_render and bolt.hide_render and fragment.hide_render
baseline = scene.view_settings.exposure
scene.frame_set(197)
assert rock.hide_render and not bolt.hide_render and not fragment.hide_render
assert scene.view_settings.exposure > baseline + 1
start = fragment.location.copy()
scene.frame_set(216)
assert bolt.hide_render and not fragment.hide_render and (fragment.location - start).length > 1
scene.frame_set(229)
assert rock.hide_render and bolt.hide_render and fragment.hide_render
print('Verified ridge strike visibility and fragment movement', flush=True)

output = Path(__file__).resolve().parent / 'work' / 'impact_frames'
output.mkdir(exist_ok=True)
scene.frame_start = 145
scene.frame_end = 228
scene.frame_set(145)
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.compression = 15
scene.render.filepath = str(output / 'impact-')
bpy.ops.render.render(animation=True)

from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view


scene = bpy.context.scene
rock = bpy.data.objects['FX_Roadside_Intact_Rock']
lightning = bpy.data.objects['FX_Roadside_Strike_Core']
vehicle = bpy.data.objects['Harvester_Root']
shard = bpy.data.objects['FX_Roadside_Shard_00']
scene.frame_set(178)
assert not rock.hide_render and lightning.hide_render and shard.hide_render
view = world_to_camera_view(scene, scene.camera, rock.matrix_world.translation)
assert 0.2 < view.x < 0.8 and 0.2 < view.y < 0.8 and view.z > 0
scene.frame_set(179)
assert rock.hide_render and not lightning.hide_render and not shard.hide_render
scene.frame_set(228)
rest = shard.location.copy()
scene.frame_set(229)
assert scene.camera.name == 'CAM_S01-030' and (shard.location - rest).length < 0.001
scene.frame_set(291)
assert shard.location.x - rest.x > 0.4 and shard.scale.z < 0.65
assert vehicle.location.y - 4.94 > 75.55
scene.frame_set(301)
assert scene.camera.name == 'CAM_S01-040'
print('Verified the strike, persistent debris, tread crossing and medium-shot cut', flush=True)

task_dir = Path(__file__).resolve().parent
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.compression = 15
if 'samples' in sys.argv:
    output = task_dir / 'work' / 'roadside_checks'
    output.mkdir(exist_ok=True)
    scene.render.resolution_percentage = 38
    for frame in (145, 179, 191, 229, 251, 261, 269, 290, 301, 390):
        scene.frame_set(frame)
        scene.render.filepath = str(output / f'roadside-{frame:04}.png')
        bpy.ops.render.render(write_still=True)
else:
    output = task_dir / 'work' / 'roadside_frames'
    output.mkdir(exist_ok=True)
    scene.frame_start = 145
    scene.frame_end = 432
    scene.frame_set(145)
    scene.render.filepath = str(output / 'roadside-')
    bpy.ops.render.render(animation=True)

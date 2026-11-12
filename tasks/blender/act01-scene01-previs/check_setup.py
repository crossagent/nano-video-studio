from pathlib import Path

import bpy


scene = bpy.context.scene
expected_markers = [('S01-010', 1), ('S01-020', 145), ('S01-030', 229), ('S01-040', 301)]
markers = sorted(scene.timeline_markers, key=lambda marker: marker.frame)
assert [(marker.name, marker.frame) for marker in markers] == expected_markers
assert (scene.frame_start, scene.frame_end) == (1, 432)
assert (scene.render.resolution_x, scene.render.resolution_y, scene.render.fps) == (1920, 804, 24)

terrain = bpy.data.objects['S01_Continuous_Canyon']


def ground(x, y):
    hit, point, _, _ = terrain.ray_cast((x, y, 200), (0, 0, -1))
    assert hit, f'Outside canyon terrain: {x:.1f}, {y:.1f}'
    return point.z


assert min(ground(-170, 145), ground(170, 145)) > 45
assert abs(ground(58, 330)) < 1
for frame in range(scene.frame_start, scene.frame_end + 1):
    scene.frame_set(frame)
    x, y, z = scene.camera.matrix_world.translation
    assert z - ground(x, y) > 0.5, f'Camera intersects terrain at frame {frame}'
    if frame >= 229:
        x, y, z = bpy.data.objects['Harvester_Root'].matrix_world.translation
        assert abs(z - ground(x, y)) < 0.3, f'Harvester is off the road at frame {frame}'

task_dir = Path(__file__).resolve().parent
checks = task_dir / 'work' / 'checks'
checks.mkdir(exist_ok=True)
scene.render.resolution_percentage = 30
scene.render.image_settings.file_format = 'PNG'
for marker, last, sample in zip(markers, (144, 228, 300, 432), (50, 145, 288, 380)):
    for frame in (marker.frame, last):
        scene.frame_set(frame)
        assert scene.camera == marker.camera, f'Wrong camera at frame {frame}'
    scene.frame_set(sample)
    scene.render.filepath = str(checks / f'{marker.name}.png')
    bpy.ops.render.render(write_still=True)
    print(f'{marker.name}: {marker.frame}–{last}, sample {sample}', flush=True)

output = task_dir / 'output'
output.mkdir(exist_ok=True)
scene.frame_set(340)
scene.timeline_markers.clear()
scene.render.resolution_percentage = 100
for name, filename, resolution in [
    ('CAM_S01_Canyon_Overview', 'canyon-overview.png', (1400, 1000)),
    ('CAM_S01_Canyon_Plan', 'canyon-plan.png', (1100, 1100)),
]:
    scene.camera = bpy.data.objects[name]
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.filepath = str(output / filename)
    bpy.ops.render.render(write_still=True)

print('Validated four cameras, vehicle route and canyon clearance over 432 frames', flush=True)

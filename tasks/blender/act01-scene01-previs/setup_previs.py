from pathlib import Path
import sys

import bpy
from mathutils import Vector


task_dir = Path(__file__).resolve().parent
sys.path[:0] = [str(task_dir), str(task_dir.parents[2] / 'platform' / 'blender')]
import previs_toolkit as previs
from canyon_set import build_canyon


def collection(name):
    group = bpy.data.collections.new(name)
    scene.collection.children.link(group)
    return group


def camera(shot, focal_length, poses):
    name = f'CAM_{shot}'
    cam = previs.create_previs_camera(name, poses[0][1], (0, 0, 0), focal_length, collection=cameras)
    cam.data.clip_start = 0.05
    cam.rotation_mode = 'QUATERNION'
    previous_rotation = None
    for frame, position, target in poses:
        cam.location = position
        rotation = (Vector(target) - cam.location).to_track_quat('-Z', 'Y')
        if previous_rotation is not None and rotation.dot(previous_rotation) < 0:
            rotation.negate()
        cam.rotation_quaternion = rotation
        previous_rotation = rotation
        cam.keyframe_insert(data_path='location', frame=frame)
        cam.keyframe_insert(data_path='rotation_quaternion', frame=frame)
    marker = scene.timeline_markers.new(shot, frame=poses[0][0])
    marker.camera = cam


def survey_camera(name, position, target, scale, group):
    cam = previs.create_previs_camera(name, position, (0, 0, 0), collection=group)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = scale
    if position[:2] != target[:2]:
        cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()


def linear_motion(obj):
    animation = obj.animation_data
    for layer in animation.action.layers:
        for strip in layer.strips:
            channel = strip.channelbag(animation.action_slot)
            for curve in channel.fcurves:
                for key in curve.keyframe_points:
                    key.interpolation = 'LINEAR'


scene = previs.init_previs_scene(clear_defaults=False)
vehicle = bpy.data.objects['Harvester_Root']
parts = [vehicle, *vehicle.children_recursive]
for child in list(scene.collection.children):
    scene.collection.children.unlink(child)
for obj in list(scene.collection.objects):
    scene.collection.objects.unlink(obj)

scene.name = 'ACT01_Scene01_Previs'
scene.frame_start = 1
scene.frame_end = 432
scene.render.fps_base = 1.0
scene.timeline_markers.clear()
scene['storyboard'] = 'assets/storyboards/act-01-storyboard-script.md | Scene 1 v001'
scene['stage'] = 'Continuous canyon set with four storyboard cameras'
scene.unit_settings.system = 'METRIC'
scene.display.shading.background_type = 'WORLD'
world = bpy.data.worlds.new('S01_Storm_Background')
world.color = (0.07, 0.08, 0.09)
scene.world = world

build_canyon(collection('S01_Canyon_Terrain'), collection('S01_Valley_Floor_Details'))
cameras = collection('S01_Shot_Cameras')
surveys = collection('S01_Site_Overview_Cameras')
survey_camera('CAM_S01_Canyon_Overview', (480, -405, 540), (0, 145, 16), 1020, surveys)
survey_camera('CAM_S01_Canyon_Plan', (0, 150, 680), (0, 150, 0), 675, surveys)
vehicle_group = collection('S01_Harvester')
for obj in parts:
    obj.animation_data_clear()
    vehicle_group.objects.link(obj)

for frame, position in [
    (1, (390, 54, 0)),
    (228, (390, 54, 0)),
    (229, (24, 54, 0)),
    (300, (24, 86, 0)),
    (301, (24, 87, 0)),
    (432, (24, 189, 0)),
]:
    vehicle.location = position
    vehicle.keyframe_insert(data_path='location', frame=frame)
linear_motion(vehicle)

camera('S01-010', 24, [
    (1, (-12, -78, 108), (-7, 8, 48)),
    (43, (-10, -20, 79), (0, 133, 22)),
    (78, (-4, 28, 36), (3, 75, 0)),
    (110, (2, 59, 5), (4, 93, 0.8)),
    (144, (4, 87, 1.4), (4, 118, 1.2)),
])
camera('S01-020', 18, [(145, (4, 89, 1.4), (-28, 2, 34))])
camera('S01-030', 28, [(229, (34, 104, 1.7), (24, 68, 2.1))])
camera('S01-040', 30, [
    (301, (42, 75, 5.2), (24, 87, 2.2)),
    (432, (42, 177, 5.2), (24, 189, 2.2)),
])
linear_motion(bpy.data.objects['CAM_S01-040'])

scene.frame_set(1)
scene.camera = bpy.data.objects['CAM_S01-010']
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'

work = task_dir / 'work'
work.mkdir(exist_ok=True)
scene.render.filepath = '//../output/act01_scene01_previs'
bpy.ops.wm.save_as_mainfile(filepath=str(work / 'act01_scene01_canyon.blend'))
print(f'Scene 1 canyon saved with {len(parts)} reused vehicle objects', flush=True)

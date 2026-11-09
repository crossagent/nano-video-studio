import bpy
from mathutils import Matrix
from pathlib import Path

ROOT = Path(r'D:\nano-video-studio\tasks\blender\act01-shared-world')
(ROOT / 'work').mkdir(parents=True, exist_ok=True)
(ROOT / 'output' / 'checks').mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene

def anchor(name, collection_name, offset, cameras):
    coll = bpy.data.collections[collection_name]
    obj = bpy.data.objects.new(name, None)
    scene.collection.objects.link(obj)
    obj.empty_display_type = 'CIRCLE'
    obj.empty_display_size = 4
    # Parent only root objects, preserving the existing parent hierarchies and animations.
    for member in list(coll.objects):
        if member.parent is None:
            member.parent = obj
            member.matrix_parent_inverse = Matrix.Identity(4)
    for name in cameras:
        camera = bpy.data.objects[name]
        camera.parent = obj
        camera.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = offset
    return obj

anchor('WORLD_02_FreeHaven', 'Set_B_FreeHaven_Perimeter', (-100, 0, 0), ['Cam_05_TurretPerimeter'])
anchor('WORLD_03_Homestead', 'Set_C_Homestead_Interior', (-370, -10, 0),
       ['Cam_07_HomesteadLock', 'Cam_09_SeismographECU', 'Cam_10_HomesteadQuake'])
anchor('WORLD_04_Temple', 'Set_D_XelNagaTemple_Chasm', (-500, 0, 0),
       ['Cam_15_TempleChasmEpic', 'Cam_19_CosmicBeacon'])

# The cockpit geometry is already parented to the moving harvester. The camera
# keys are expressed in that same local cockpit space; make it travel with it.
cockpit = bpy.data.objects['Cam_03_CockpitMS']
cockpit.parent = bpy.data.objects['Harvester_Root']
cockpit.matrix_parent_inverse = Matrix.Identity(4)
cockpit.data.lens = 18

def aim(camera, target):
    from mathutils import Vector
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()

# The source camera starts inside the harvester at frame 1. Move it aside,
# and aim the tracking camera far enough back to show the vehicle as a whole.
cam = bpy.data.objects['Cam_01_StormWide']
cam.location = (-23, 36, 2.8)
for frame, target in [(1, (0, -55, 16)), (72, (0, -35, 26))]:
    aim(cam, target)
    cam.keyframe_insert(data_path='rotation_euler', frame=frame)
cam = bpy.data.objects['Cam_02_HarvesterTrack']
for frame, y in [(73, 38), (144, -20)]:
    cam.location = (-19, y + 12, 6.0)
    aim(cam, (0, y, 2.5))
    cam.keyframe_insert(data_path='location', frame=frame)
    cam.keyframe_insert(data_path='rotation_euler', frame=frame)

# The original cabin was a solid cube enclosing both performers. Replace its
# opaque walls with a roof and corner posts while keeping the exterior volume.
cab = next(o for o in bpy.data.collections['Set_A_BhekarRo_Plains'].objects
           if o.parent and o.parent.name == 'Harvester_Root' and o.type == 'MESH'
           and all(abs(a-b) < 0.02 for a,b in zip(o.scale, (3.4, 3.4, 2.0))))
cab.hide_render = True
cab.hide_viewport = True
cab['reason'] = 'Replaced by open cabin frame so interior and exterior share one vehicle.'
def cabin_piece(name, loc, scale):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.name = name
    obj.parent = bpy.data.objects['Harvester_Root']
    obj.location = loc
    obj.scale = scale
    if cab.data.materials: obj.data.materials.append(cab.data.materials[0])
    coll = bpy.data.collections['Set_A_BhekarRo_Plains']
    for c in list(obj.users_collection): c.objects.unlink(obj)
    coll.objects.link(obj)
for x in (-1.6, 1.6):
    for y in (-0.1, 3.05): cabin_piece('Cabin_Frame_Post', (x, y, 3.6), (0.14, 0.14, 2.0))
cabin_piece('Cabin_Frame_Roof', (0, 1.5, 4.6), (3.4, 3.4, 0.15))
for frame in range(145, 217, 3):
    q = (frame % 4 - 2) * 0.025
    cockpit.location = (q, 3.0, 4.25 + q)
    aim(cockpit, (0, 1.45, 3.65))
    cockpit.keyframe_insert(data_path='location', frame=frame)
    cockpit.keyframe_insert(data_path='rotation_euler', frame=frame)

# The source used a full-size human dummy as a stand-in for a close-up hand on
# the workbench; it appears as an extra person in wider shots. Hide the stand-in.
hand = bpy.data.objects.get('Lars_CloseArm')
if hand:
    for obj in [hand] + list(hand.children_recursive):
        obj.hide_render = True
        obj.hide_viewport = True

# The separate planet must not appear in Bhekar Ro shots even at long clip distances.
for obj in bpy.data.collections['Set_E_PlanetChar'].objects:
    for frame, hidden in [(1, True), (504, True), (505, False), (576, False), (577, True)]:
        obj.hide_render = hidden
        obj.keyframe_insert(data_path='hide_render', frame=frame)

# Home cameras are local to the relocated home anchor. Aim toward the shared
# actors/workbench instead of the blank wall and the instrument's near surface.
cam = bpy.data.objects['Cam_07_HomesteadLock']
cam.location = (496.7, -2.9, 2.25)
aim(cam, (501, 0.2, 1.55))
cam.keyframe_insert(data_path='location', frame=289)
cam.keyframe_insert(data_path='rotation_euler', frame=289)
cam = bpy.data.objects['Cam_09_SeismographECU']
for frame in range(361, 433, 4):
    q = (frame % 3 - 1) * 0.015
    cam.location = (500.7 + q, -2.3, 2.65)
    aim(cam, (502.3, -0.4, 2.15))
    cam.keyframe_insert(data_path='location', frame=frame)
    cam.keyframe_insert(data_path='rotation_euler', frame=frame)

# Continuous simple terrain fills the gap between the town and the temple set.
bpy.ops.mesh.primitive_plane_add(size=2, location=(225, 0, -0.04))
bridge = bpy.context.object
bridge.name = 'WORLD_BhekarRo_Town_to_Chasm_Terrain'
bridge.scale = (25, 60, 1)
source = bpy.data.objects.get('Plains_Ground_Wheat')
if source and source.data.materials:
    bridge.data.materials.append(source.data.materials[0])
world_coll = bpy.data.collections.new('WORLD_BhekarRo_Connections')
scene.collection.children.link(world_coll)
for c in list(bridge.users_collection): c.objects.unlink(bridge)
world_coll.objects.link(bridge)

scene.frame_set(1)
scene.camera = bpy.data.objects['Cam_01_StormWide']
scene.render.resolution_x = 1920
scene.render.resolution_y = 804
scene.render.resolution_percentage = 100
scene.render.fps = 24
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'work' / 'act01_shared_world.blend'))

# Representative frames are review aids, kept separate from the 1920x804 master.
scene.render.resolution_percentage = 50
scene.render.image_settings.file_format = 'PNG'
for shot, frame in enumerate([1, 73, 145, 217, 289, 361, 433, 505, 577, 673], 1):
    scene.frame_set(frame)
    scene.render.filepath = str(ROOT / 'output' / 'checks' / f'shot_{shot:02d}_frame_{frame:03d}.png')
    bpy.ops.render.render(write_still=True)
    print('CHECK_RENDER', shot, frame, scene.camera.name if scene.camera else 'NONE', flush=True)

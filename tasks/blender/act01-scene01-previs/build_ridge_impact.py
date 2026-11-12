from math import radians
from pathlib import Path
from random import Random
import sys

import bmesh
import bpy
from mathutils import Vector


task_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(task_dir.parents[2] / 'platform' / 'blender'))
from previs_toolkit import create_previs_material


def ground(x, y):
    hit, point, _, _ = terrain.ray_cast((x, y, 200), (0, 0, -1))
    if not hit:
        raise RuntimeError(f'No terrain under impact at {(x, y)}')
    return point.z


def visibility(obj, start, stop):
    for frame, hidden in [(1, True), (start, False), (stop, True)]:
        for prop in ('hide_render', 'hide_viewport'):
            setattr(obj, prop, hidden)
            obj.keyframe_insert(data_path=prop, frame=frame)


def stone(name, size, position):
    geometry = bmesh.new()
    bmesh.ops.create_icosphere(geometry, subdivisions=2, radius=1)
    for vertex in geometry.verts:
        vertex.co *= rng.uniform(0.72, 1.16)
    mesh = bpy.data.meshes.new(name)
    geometry.to_mesh(mesh)
    geometry.free()
    mesh.materials.append(rock)
    mesh.materials.append(fresh_rock)
    for face in mesh.polygons:
        face.material_index = int(face.normal.z > 0.28)
    obj = bpy.data.objects.new(name, mesh)
    obj.scale = size
    obj.location = position
    effects.objects.link(obj)
    return obj


def beam(name, points, radius, material):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 1
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for point, xyz in zip(spline.points, points):
        point.co = (*xyz, 1)
    curve.materials.append(material)
    obj = bpy.data.objects.new(name, curve)
    effects.objects.link(obj)
    visibility(obj, strike, strike + 3)
    return obj


def animate_fragment(index):
    radius = rng.uniform(0.65, 1.15) if index < 8 else rng.uniform(0.18, 0.65)
    offset = Vector((rng.uniform(-2.0, 2.0), rng.uniform(-0.8, 0.9), rng.uniform(-0.8, 1.5)))
    position = impact + offset
    size = (radius * rng.uniform(0.8, 1.45), radius, radius * rng.uniform(0.65, 1.15))
    position.z = max(position.z, ground(position.x, position.y) + size[2])
    obj = stone(f'FX_S01_Ridge_Fragment_{index:02}', size, position)
    velocity = Vector((rng.uniform(-13, 13), rng.uniform(3, 17), rng.uniform(-3, 13)))
    spin = Vector((rng.uniform(-9, 9), rng.uniform(-8, 8), rng.uniform(-8, 8)))
    rotation = Vector(tuple(rng.uniform(-1, 1) for _ in range(3)))
    for frame in range(strike, shot_end + 1):
        obj.location = position
        obj.rotation_euler = rotation
        obj.keyframe_insert(data_path='location', frame=frame)
        obj.keyframe_insert(data_path='rotation_euler', frame=frame)
        velocity.z -= 22 / 24
        position += velocity / 24
        rotation += spin / 24
        floor = ground(position.x, position.y) + size[2] * 0.75
        if position.z < floor:
            position.z = floor
            velocity.z = abs(velocity.z) * 0.27
            velocity.x *= 0.82
            velocity.y *= 0.82
            spin *= 0.74
    visibility(obj, strike, shot_end + 1)


rng = Random(713)
scene = bpy.context.scene
terrain = bpy.data.objects['S01_Continuous_Canyon']
effects = bpy.data.collections.new('S01-020 | Ridge Strike and Fracture')
scene.collection.children.link(effects)
rock = create_previs_material('S01_Impact_Basalt', (0.22, 0.23, 0.25, 1))
fresh_rock = create_previs_material('S01_Impact_Fresh_Fracture', (0.49, 0.46, 0.43, 1))
core = create_previs_material('S01_Lightning_Core', (1.0, 0.96, 1.0, 1))
edge = create_previs_material('S01_Lightning_Edge', (0.58, 0.43, 0.98, 1))
strike = 197
shot_end = 228
impact = Vector((-31.0, 17.0, ground(-31, 17) + 2.5))

outcrop = stone('FX_S01_Intact_Outcrop', (3.1, 2.7, 2.9), impact - Vector((0, 0, 0.6)))
outcrop.rotation_euler = (radians(12), radians(-14), radians(18))
visibility(outcrop, 145, strike)
remnant = stone('FX_S01_Fractured_Stump', (2.55, 2.0, 1.15), impact - Vector((0.3, 0.1, 1.7)))
visibility(remnant, strike, shot_end + 1)

points = [impact + Vector(offset) for offset in [
    (8, -8, 92), (4, -4, 69), (6, -3, 53), (0, -4, 36), (2, 1, 20), (-1.5, 1.2, 9), (0, 0, 0),
]]
beam('FX_S01_Lightning_Core', points, 0.26, core)
beam('FX_S01_Lightning_Fringe', [point + Vector((0.10, -0.30, 0)) for point in points], 0.35, edge)
beam('FX_S01_Lightning_Fork', [points[2], points[2] + Vector((-7, 0, -8)),
                               points[2] + Vector((-9, 0, -20))], 0.095, edge)
flash = stone('FX_S01_Contact_Flash', (1.65, 1.3, 1.35), impact)
flash.data.materials.clear()
flash.data.materials.append(core)
visibility(flash, strike, strike + 2)
for index in range(34):
    animate_fragment(index)

exposure = scene.view_settings.exposure
for frame, boost in [(strike - 1, 0), (strike, 1.2), (strike + 1, 0.65), (strike + 2, 0.25), (strike + 3, 0)]:
    scene.view_settings.exposure = exposure + boost
    scene.keyframe_insert(data_path='view_settings.exposure', frame=frame)

scene['stage'] = 'Canyon with animated S01-020 lightning and ridge fracture'
scene['ridge_strike_frame'] = strike
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(task_dir / 'work' / 'act01_scene01_canyon_impact.blend'))
print('Ridge impact saved: frame 197, 34 animated rock fragments', flush=True)

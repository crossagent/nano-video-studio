from math import ceil, cos, floor, pi, sin, tau
from pathlib import Path
from random import Random
import sys

import bmesh
import bpy
from mathutils import Euler, Vector


task_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(task_dir.parents[2] / 'platform' / 'blender'))
from previs_toolkit import create_previs_material


def mesh_object(name, vertices, faces, materials, group):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    for material in materials:
        mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    group.objects.link(obj)
    return obj


def show_between(obj, start, stop):
    for frame, hidden in [(1, True), (start, False), (stop, True)]:
        for prop in ('hide_render', 'hide_viewport'):
            setattr(obj, prop, hidden)
            obj.keyframe_insert(data_path=prop, frame=frame)


def aim(cam, position, target, lens):
    cam.animation_data_clear()
    cam.data.lens = lens
    cam.data.clip_start = 0.04
    cam.location = position
    cam.rotation_mode = 'QUATERNION'
    cam.rotation_quaternion = (Vector(target) - cam.location).to_track_quat('-Z', 'Y')


def bolt(name, offsets, radius, material):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    path = curve.splines.new('POLY')
    path.points.add(len(offsets) - 1)
    for point, offset in zip(path.points, offsets):
        point.co = (*(hit_point + Vector(offset)), 1)
    curve.materials.append(material)
    obj = bpy.data.objects.new(name, curve)
    effects.objects.link(obj)
    show_between(obj, strike, strike + 3)


def pose(obj, frame, position, rotation, scale=1.0):
    obj.location = position
    obj.rotation_euler = rotation
    obj.scale = (scale,) * 3
    for prop in ('location', 'rotation_euler', 'scale'):
        obj.keyframe_insert(data_path=prop, frame=frame)


def rest_height(vertices, rotation, scale=1.0):
    matrix = Euler(rotation).to_matrix()
    return road_surface - min((matrix @ vertex).z for vertex in vertices) * scale


def split_rock(geometry):
    seeds = [Vector((rng.uniform(-0.67, 0.67), rng.uniform(-0.53, 0.53), rng.uniform(-0.53, 0.53)))
             for _ in range(20)]
    pieces = []
    for seed in seeds:
        piece = geometry.copy()
        for other in seeds:
            if other is seed:
                continue
            result = bmesh.ops.bisect_plane(
                piece, geom=[*piece.verts, *piece.edges, *piece.faces], dist=0.0001,
                plane_co=(seed + other) / 2, plane_no=(other - seed).normalized(), clear_outer=True,
            )
            border = [edge for edge in result['geom_cut'] if isinstance(edge, bmesh.types.BMEdge) and edge.is_boundary]
            if border:
                for face in bmesh.ops.holes_fill(piece, edges=border)['faces']:
                    face.material_index = 1
        if piece.faces:
            bmesh.ops.recalc_face_normals(piece, faces=list(piece.faces))
            center = sum((vertex.co for vertex in piece.verts), Vector()) / len(piece.verts)
            for vertex in piece.verts:
                vertex.co -= center
            pieces.append((piece.calc_volume(), center, piece))
        else:
            piece.free()
    return sorted(pieces, key=lambda item: item[0], reverse=True)


def fragment(index, center, piece):
    name = f'FX_Roadside_Shard_{index:02}'
    mesh = bpy.data.meshes.new(name)
    local = [vertex.co.copy() for vertex in piece.verts]
    piece.to_mesh(mesh)
    piece.free()
    for material in (basalt, fracture):
        mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    effects.objects.link(obj)
    bevel = obj.modifiers.new('Small broken edges', 'BEVEL')
    bevel.width = 0.018
    bevel.segments = 1
    show_between(obj, strike, 433)

    on_track = index < 15
    x = track_x + (rng.uniform(-0.36, 0.42) if on_track else rng.choice((-1, 1)) * rng.uniform(0.85, 1.55))
    y = rock_y + rng.uniform(-1.25, 1.55)
    initial = rock_center + center
    final_rotation = tuple(rng.uniform(-2, 2) for _ in range(3))
    landing = Vector((x, y, rest_height(local, final_rotation)))
    settle = strike + rng.randint(17, 25)
    arc = rng.uniform(0.25, 0.78)
    for frame in range(strike, settle, 3):
        t = (frame - strike) / (settle - strike)
        point = initial.lerp(landing, t)
        point.z += 4 * arc * t * (1 - t)
        pose(obj, frame, point, tuple(angle * t for angle in final_rotation))
    pose(obj, settle, landing, final_rotation)

    if on_track:
        contact = ceil(229 + (y - 4.92 - 54) * 71 / 32)
        pose(obj, contact - 1, landing, final_rotation)
        roll = (final_rotation[0] + 1.1, final_rotation[1] - 0.65, final_rotation[2] + 0.4)
        pose(obj, contact + 1, (x + 0.10, y + 0.14, rest_height(local, roll, 0.58)), roll, 0.58)
        size = rng.uniform(0.28, 0.43)
        pose(obj, contact + 7, (track_x + rng.uniform(0.8, 1.35), y + rng.uniform(0.25, 0.95),
                                rest_height(local, roll, size)), roll, size)


def build_track_links():
    group = bpy.data.collections.new('S01-030 | Right Tread Links')
    scene.collection.children.link(group)
    vertices = [(x, y, z) for z in (-0.07, 0.07) for y in (-0.108, 0.108) for x in (-0.70, 0.70)]
    faces = [(1, 0, 2, 3), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    prototype = mesh_object('FX_Tread_Link_00', vertices, faces, (tread_material,), group)
    links = [prototype]
    for index in range(1, 68):
        link = bpy.data.objects.new(f'FX_Tread_Link_{index:02}', prototype.data)
        group.objects.link(link)
        links.append(link)

    axle, radius, center_z = 4.07, 0.87, 1.05
    straight, arc = 2 * axle, pi * radius
    circuit = 2 * (straight + arc)
    for index, link in enumerate(links):
        link.parent = vehicle
        for frame in range(229, 433):
            distance = (frame - 229) * 32 / 71 if frame <= 300 else 33 + (frame - 301) * 102 / 131
            phase = index * circuit / len(links) + distance
            lap = floor(phase / circuit)
            s = phase - lap * circuit
            if s < straight:
                y, z, angle = axle - s, center_z - radius, 0
            elif s < straight + arc:
                t = (s - straight) / radius
                y, z, angle = -axle - radius * sin(t), center_z - radius * cos(t), -t
            elif s < 2 * straight + arc:
                y, z, angle = -axle + s - straight - arc, center_z + radius, -pi
            else:
                t = (s - 2 * straight - arc) / radius
                y, z, angle = axle + radius * sin(t), center_z + radius * cos(t), -pi - t
            link.location = (2.85, y, z)
            link.rotation_euler.x = angle - tau * lap
            link.keyframe_insert(data_path='location', frame=frame)
            link.keyframe_insert(data_path='rotation_euler', frame=frame, index=0)


scene = bpy.context.scene
vehicle = bpy.data.objects['Harvester_Root']
effects = bpy.data.collections.new('S01-020–030 | Roadside Strike and Fragments')
scene.collection.children.link(effects)
rng = Random(622)
basalt = create_previs_material('S01_Roadside_Basalt', (0.34, 0.30, 0.27, 1))
fracture = create_previs_material('S01_New_Fracture', (0.60, 0.54, 0.48, 1))
tread_material = create_previs_material('S01_Tread_Link_Metal', (0.16, 0.17, 0.18, 1))
white = create_previs_material('S01_Road_Strike_Core', (1, 0.99, 1, 1))
violet = create_previs_material('S01_Road_Strike_Fork', (0.62, 0.51, 1, 1))
strike = 179
track_x, rock_y, road_surface = 26.85, 74.0, 0.10

geometry = bmesh.new()
bmesh.ops.create_icosphere(geometry, subdivisions=2, radius=1)
geometry.verts.ensure_lookup_table()
geometry.verts.index_update()
for vertex in geometry.verts:
    vertex.co *= rng.uniform(0.91, 1.08)
    vertex.co.x *= 1.03
    vertex.co.y *= 0.82
    vertex.co.z *= 0.75
geometry.normal_update()
vertices = [vertex.co.copy() for vertex in geometry.verts]
faces = [tuple(vertex.index for vertex in face.verts) for face in geometry.faces]
pieces = split_rock(geometry)
geometry.free()
rock_center = Vector((track_x, rock_y, rest_height(vertices, (0, 0, 0))))
intact = mesh_object('FX_Roadside_Intact_Rock', vertices, faces, (basalt,), effects)
intact.location = rock_center
show_between(intact, 145, strike)
hit_point = rock_center + max(vertices, key=lambda vertex: vertex.z)

path = [(0.5, -0.15, 19), (0.27, 0.2, 10), (-0.19, -0.04, 5.1),
        (0.13, 0.08, 2.35), (-0.12, 0.10, 1.1), (0.02, 0.04, 0.37), (0, 0, 0)]
bolt('FX_Roadside_Strike_Core', path, 0.045, white)
bolt('FX_Roadside_Strike_Fork', [path[3], (0.67, 0.08, 1.6), (0.84, 0.12, 0.92)], 0.019, violet)
for index, (_, center, piece) in enumerate(pieces):
    fragment(index, center, piece)

aim(bpy.data.objects['CAM_S01-020'], (29.65, 78.1, 0.84), (26.85, 74, 0.83), 36)
aim(bpy.data.objects['CAM_S01-030'], (32.2, 75.8, 1.02), (26.72, 74.15, 0.68), 29)
medium = bpy.data.objects['CAM_S01-040']
medium.parent = vehicle
aim(medium, (10.8, -7.5, 3.9), (0, 0.6, 2.6), 35)
build_track_links()

for frame, exposure in [(178, 0), (179, 1.35), (180, 0.8), (181, 0.3), (182, 0)]:
    scene.view_settings.exposure = exposure
    scene.keyframe_insert(data_path='view_settings.exposure', frame=frame)

scene['stage'] = 'Roadside rock close-up, tread crossing, vehicle medium shot'
scene['roadside_strike_frame'] = strike
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(task_dir / 'work' / 'act01_scene01_roadside_strike.blend'))
print('Roadside strike project saved', flush=True)

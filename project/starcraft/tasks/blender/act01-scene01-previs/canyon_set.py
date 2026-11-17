from math import cos, sin

import bpy
from mathutils.bvhtree import BVHTree

from previs_toolkit import create_previs_material


def smoothstep(start, end, value):
    t = max(0.0, min(1.0, (value - start) / (end - start)))
    return t * t * (3 - 2 * t)


def road_center(y):
    return 24 + 34 * smoothstep(205, 328, y)


def channel_center(y):
    return -36 + 12 * sin((y - 65) / 34)


def terrain_height(x, y):
    valley_center = -12 + 23 * sin((y - 40) / 112)
    east = x > valley_center
    half_width = (106 if east else 95) + 13 * sin(y / 45 + (0.7 if east else 2.1))
    wall_distance = abs(x - valley_center) - half_width
    talus = 23 * smoothstep(0, 37, wall_distance)
    cliff = 63 + 15 * sin(y / 25 + x / 40)
    cliff += 8 * sin(y / 10 + x / 28 + (0.0 if east else 1.9)) + 7 * cos(x / 23 + y / 38)
    cliff *= smoothstep(24, 65, wall_distance)

    ridge_line = 9 * sin(x / 37) + 6 * sin(x / 72)
    saddle = smoothstep(5, 34, abs(x + 9))
    crest = 27 + (45 + 9 * cos(x / 11) + 8 * sin(x / 6)) * saddle
    windward_ridge = crest * (1 - smoothstep(0, 43, abs(y - ridge_line)))
    outlet = smoothstep(11, 52, abs(x - road_center(y)))
    outlet_ridge = (37 + 13 * sin(x / 17)) * outlet * (1 - smoothstep(0, 48, abs(y - 330)))

    off_road = smoothstep(6, 20, abs(x - road_center(y)))
    floor = (0.35 * sin(x / 15 + y / 22) + 0.22 * cos(y / 17)) * off_road
    channel = (1 - smoothstep(0, 7, abs(x - channel_center(y))))
    channel *= smoothstep(28, 55, y) * (1 - smoothstep(290, 329, y))
    return floor - 1.2 * channel + max(talus + cliff, windward_ridge, outlet_ridge)


def mesh_object(name, vertices, faces, materials, group):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    for material in materials:
        mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    group.objects.link(obj)
    return obj


def add_ribbon(vertices, faces, segments, ground_at):
    start = len(vertices)
    for y, left, right, height in segments:
        vertices.extend((x, y, ground_at(x, y) + height) for x in (left, right))
    faces.extend((i, i + 1, i + 3, i + 2) for i in range(start, len(vertices) - 2, 2))


def build_canyon(landscape, floor_details):
    rock = create_previs_material('S01_Basalt', (0.09, 0.11, 0.14, 1))
    slope = create_previs_material('S01_Talus', (0.17, 0.18, 0.18, 1))
    floor = create_previs_material('S01_Valley_Floor', (0.32, 0.27, 0.19, 1))
    fields = create_previs_material('S01_Wheat_Beds', (0.48, 0.37, 0.19, 1))
    mud = create_previs_material('S01_Road_Mud', (0.22, 0.17, 0.13, 1))
    ruts = create_previs_material('S01_Wheel_Ruts', (0.13, 0.11, 0.09, 1))
    drainage = create_previs_material('S01_Drainage', (0.15, 0.18, 0.15, 1))

    xs = list(range(-320, 321, 4))
    ys = list(range(-160, 461, 4))
    width = len(xs)
    vertices = [(x, y, terrain_height(x, y)) for y in ys for x in xs]
    faces = []
    for row in range(len(ys) - 1):
        for column in range(width - 1):
            index = row * width + column
            faces.append((index, index + 1, index + width + 1, index + width))
    surface_faces = len(faces)
    height_count = len(ys)
    boundary = list(range(width))
    boundary.extend(row * width + width - 1 for row in range(1, height_count))
    boundary.extend((height_count - 1) * width + col for col in range(width - 2, -1, -1))
    boundary.extend(row * width for row in range(height_count - 2, 0, -1))
    base = list(range(len(vertices), len(vertices) + len(boundary)))
    vertices.extend((vertices[index][0], vertices[index][1], -18) for index in boundary)
    for i, top in enumerate(boundary):
        next_i = (i + 1) % len(boundary)
        faces.append((boundary[next_i], top, base[i], base[next_i]))
    faces.append(tuple(reversed(base)))
    terrain = mesh_object('S01_Continuous_Canyon', vertices, faces, (floor, slope, rock), landscape)
    for polygon in terrain.data.polygons:
        height = polygon.center.z
        polygon.material_index = 2 if polygon.index >= surface_faces or height > 25 else 1 if height > 5 else 0
    terrain_surface = BVHTree.FromPolygons(vertices, faces)

    def ground_at(x, y):
        position, _, _, _ = terrain_surface.ray_cast((x, y, 200), (0, 0, -1))
        return position.z

    vertices, faces = [], []
    add_ribbon(vertices, faces, ((y, road_center(y) - 5, road_center(y) + 5, 0.07) for y in range(37, 421, 2)), ground_at)
    mesh_object('S01_Road_To_Outlet', vertices, faces, (mud,), floor_details)

    vertices, faces = [], []
    for offset in (-2.85, 2.85):
        add_ribbon(vertices, faces, ((y, road_center(y) + offset - 0.5, road_center(y) + offset + 0.5, 0.10)
                                     for y in range(37, 421, 2)), ground_at)
    mesh_object('S01_Harvester_Ruts', vertices, faces, (ruts,), floor_details)

    vertices, faces = [], []
    for left, right, start, end in [(-75, -48, 54, 194), (-19, 13, 54, 214), (39, 78, 68, 222), (-62, -12, 222, 282)]:
        for x in range(left, right, 3):
            add_ribbon(vertices, faces, ((y, x, x + 1.45, 0.08) for y in range(start, end, 2)), ground_at)
    mesh_object('S01_Wheat_Bed_Layout', vertices, faces, (fields,), floor_details)

    vertices, faces = [], []
    add_ribbon(vertices, faces, ((y, channel_center(y) - 2, channel_center(y) + 2, 0.15) for y in range(50, 306)), ground_at)
    mesh_object('S01_Drainage_Channel', vertices, faces, (drainage,), floor_details)

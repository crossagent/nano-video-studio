import bpy
import math
import os

def setup_blender():
    # Clear all objects in current scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    
    # 2.39:1 Anamorphic Cinemascope format (1920 x 804)
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 804
    scene.render.resolution_percentage = 100
    scene.render.fps = 24
    
    # Set Workbench for crisp architectural/previs renders
    scene.render.engine = 'BLENDER_WORKBENCH'
    shading = scene.display.shading
    shading.light = 'STUDIO'
    shading.color_type = 'MATERIAL'
    shading.show_cavity = True
    shading.cavity_type = 'BOTH'
    shading.cavity_ridge_factor = 2.0
    shading.cavity_valley_factor = 1.5
    shading.show_shadows = True

def create_material(name, diffuse_color, roughness=0.5, metallic=0.0, emission_color=(0,0,0,1), emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = diffuse_color
    node_bsdf.inputs['Roughness'].default_value = roughness
    node_bsdf.inputs['Metallic'].default_value = metallic
    if 'Emission Color' in node_bsdf.inputs:
        node_bsdf.inputs['Emission Color'].default_value = emission_color
        node_bsdf.inputs['Emission Strength'].default_value = emission_strength
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    
    # Viewport color for Workbench
    mat.diffuse_color = diffuse_color
    mat.roughness = roughness
    mat.metallic = metallic
    return mat

def build_materials():
    mats = {}
    mats['Wheat'] = create_material('Mat_Wheat', (0.65, 0.52, 0.28, 1.0), roughness=0.9)
    mats['Mud'] = create_material('Mat_Mud', (0.22, 0.16, 0.12, 1.0), roughness=0.95)
    mats['RockDark'] = create_material('Mat_RockDark', (0.18, 0.17, 0.17, 1.0), roughness=0.85)
    mats['HarvesterRed'] = create_material('Mat_HarvesterRed', (0.68, 0.12, 0.15, 1.0), roughness=0.4, metallic=0.3)
    mats['Treads'] = create_material('Mat_Treads', (0.12, 0.12, 0.14, 1.0), roughness=0.7, metallic=0.8)
    mats['GlassCyan'] = create_material('Mat_GlassCyan', (0.35, 0.82, 0.90, 0.8), roughness=0.1, metallic=0.1)
    mats['MetalRust'] = create_material('Mat_MetalRust', (0.42, 0.25, 0.18, 1.0), roughness=0.7, metallic=0.4)
    mats['TurretOlive'] = create_material('Mat_TurretOlive', (0.28, 0.32, 0.22, 1.0), roughness=0.6, metallic=0.5)
    mats['XelNagaObsidian'] = create_material('Mat_XelNagaObsidian', (0.05, 0.06, 0.08, 1.0), roughness=0.2, metallic=0.9)
    mats['XelNagaGlowBlue'] = create_material('Mat_XelNagaGlowBlue', (0.1, 0.75, 1.0, 1.0), emission_color=(0.1, 0.75, 1.0, 1.0), emission_strength=5.0)
    mats['BeaconBeam'] = create_material('Mat_BeaconBeam', (0.85, 0.95, 1.0, 1.0), emission_color=(0.85, 0.95, 1.0, 1.0), emission_strength=12.0)
    mats['CharBasalt'] = create_material('Mat_CharBasalt', (0.08, 0.08, 0.09, 1.0), roughness=0.9)
    mats['CharLava'] = create_material('Mat_CharLava', (1.0, 0.28, 0.02, 1.0), emission_color=(1.0, 0.28, 0.02, 1.0), emission_strength=8.0)
    mats['ZergPurple'] = create_material('Mat_ZergPurple', (0.28, 0.12, 0.32, 1.0), roughness=0.3)
    mats['HumanSuit'] = create_material('Mat_HumanSuit', (0.85, 0.75, 0.65, 1.0), roughness=0.6)
    return mats

def create_collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

def build_set_a_plains(mats):
    col = create_collection("Set_A_BhekarRo_Plains")
    
    # Wheatfield ground
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Plains_Ground_Wheat"
    ground.data.materials.append(mats['Wheat'])
    col.objects.link(ground)
    bpy.context.scene.collection.objects.unlink(ground)
    
    # Distance mountain ridge blocks
    for i in range(-5, 6):
        x = i * 14 + (i%2)*3
        y = -55 - abs(i)*3
        h = 25 + (abs(i)*2 % 9) * 3
        w = 12 + (i % 3) * 3
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h/2))
        mountain = bpy.context.active_object
        mountain.scale = (w, 15, h)
        mountain.name = f"Mountain_Ridge_{i}"
        mountain.data.materials.append(mats['RockDark'])
        col.objects.link(mountain)
        bpy.context.scene.collection.objects.unlink(mountain)
        
    # The Robo-Harvester compound asset
    harvester_col = bpy.data.collections.new("Asset_RoboHarvester")
    col.children.link(harvester_col)
    
    # Chassis
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.8))
    chassis = bpy.context.active_object
    chassis.scale = (4.2, 8.0, 2.2)
    chassis.name = "Harvester_Chassis_Red"
    chassis.data.materials.append(mats['HarvesterRed'])
    harvester_col.objects.link(chassis)
    bpy.context.scene.collection.objects.unlink(chassis)
    
    # Tracks Left & Right
    for side, x_offset in [("Left", -2.6), ("Right", 2.6)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_offset, 0, 1.2))
        track = bpy.context.active_object
        track.scale = (1.1, 8.6, 1.8)
        track.name = f"Harvester_Track_{side}"
        track.data.materials.append(mats['Treads'])
        harvester_col.objects.link(track)
        bpy.context.scene.collection.objects.unlink(track)
        
    # Upper Cab
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 1.5, 3.4))
    cab = bpy.context.active_object
    cab.scale = (3.2, 3.2, 1.8)
    cab.name = "Harvester_Cab"
    cab.data.materials.append(mats['HarvesterRed'])
    harvester_col.objects.link(cab)
    bpy.context.scene.collection.objects.unlink(cab)
    
    # Front Viewport Glass
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 3.12, 3.5))
    glass = bpy.context.active_object
    glass.scale = (2.8, 0.1, 1.2)
    glass.name = "Harvester_Viewport_Glass"
    glass.data.materials.append(mats['GlassCyan'])
    harvester_col.objects.link(glass)
    bpy.context.scene.collection.objects.unlink(glass)
    
    # Front Harvesting Cylinder
    bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=4.6, location=(0, 4.6, 1.2))
    reel = bpy.context.active_object
    reel.rotation_euler = (0, math.radians(90), 0)
    reel.name = "Harvester_Front_Reel"
    reel.data.materials.append(mats['MetalRust'])
    harvester_col.objects.link(reel)
    bpy.context.scene.collection.objects.unlink(reel)
    
    # Mannequins inside cab (Lars & Octavia blocks)
    for name, pos_x in [("Lars", -0.8), ("Octavia", 0.8)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(pos_x, 1.5, 3.3))
        mannequin = bpy.context.active_object
        mannequin.scale = (0.5, 0.4, 0.9)
        mannequin.name = f"Figure_{name}"
        mannequin.data.materials.append(mats['HumanSuit'])
        harvester_col.objects.link(mannequin)
        bpy.context.scene.collection.objects.unlink(mannequin)

def build_set_b_free_haven(mats):
    col = create_collection("Set_B_FreeHaven_Perimeter")
    base_x = 250
    
    # Ground
    bpy.ops.mesh.primitive_plane_add(size=100, location=(base_x, 0, 0))
    ground = bpy.context.active_object
    ground.name = "FreeHaven_Ground"
    ground.data.materials.append(mats['Mud'])
    col.objects.link(ground)
    bpy.context.scene.collection.objects.unlink(ground)
    
    # Octagonal Dirt Berm ramp
    for i in range(8):
        angle = i * (2 * math.pi / 8)
        bx = base_x + math.cos(angle) * 35
        by = math.sin(angle) * 35
        bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, by, 1.5))
        berm = bpy.context.active_object
        berm.scale = (22, 4, 3)
        berm.rotation_euler = (0, 0, angle + math.pi/2)
        berm.name = f"Berm_Wall_{i}"
        berm.data.materials.append(mats['RockDark'])
        col.objects.link(berm)
        bpy.context.scene.collection.objects.unlink(berm)
        
    # Confederate Missile Turret (Iconic)
    turret_x = base_x - 5
    turret_y = 15
    
    # Pylon Tower Base
    bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=6.0, location=(turret_x, turret_y, 3.0))
    pylon = bpy.context.active_object
    pylon.name = "Turret_Pylon_Base"
    pylon.data.materials.append(mats['MetalRust'])
    col.objects.link(pylon)
    bpy.context.scene.collection.objects.unlink(pylon)
    
    # Turret Head
    bpy.ops.mesh.primitive_cube_add(size=1, location=(turret_x, turret_y, 6.8))
    head = bpy.context.active_object
    head.scale = (3.4, 2.6, 1.4)
    head.name = "Turret_Rotating_Head"
    head.data.materials.append(mats['TurretOlive'])
    col.objects.link(head)
    bpy.context.scene.collection.objects.unlink(head)
    
    # Dual Missile Pods
    for side, off in [("Left", -2.2), ("Right", 2.2)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(turret_x + off, turret_y, 7.2))
        pod = bpy.context.active_object
        pod.scale = (1.4, 3.2, 1.6)
        pod.rotation_euler = (math.radians(-15), 0, 0)
        pod.name = f"Missile_Pod_{side}"
        pod.data.materials.append(mats['TurretOlive'])
        col.objects.link(pod)
        bpy.context.scene.collection.objects.unlink(pod)
        
    # Radar Dish
    bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=0.2, location=(turret_x, turret_y, 8.4))
    dish = bpy.context.active_object
    dish.rotation_euler = (math.radians(45), 0, math.radians(30))
    dish.name = "Turret_Radar_Dish"
    dish.data.materials.append(mats['MetalRust'])
    col.objects.link(dish)
    bpy.context.scene.collection.objects.unlink(dish)
    
    # Modular Quonset Huts (Town Prefabs)
    for j, (hx, hy) in enumerate([(base_x + 10, -10), (base_x - 15, -15), (base_x + 18, 12)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=4.0, depth=14.0, location=(hx, hy, 2.0))
        hut = bpy.context.active_object
        hut.scale = (1.0, 1.0, 0.7)
        hut.rotation_euler = (math.radians(90), 0, math.radians(20*j))
        hut.name = f"Quonset_Hut_{j}"
        hut.data.materials.append(mats['MetalRust'])
        col.objects.link(hut)
        bpy.context.scene.collection.objects.unlink(hut)

def build_set_c_homestead(mats):
    col = create_collection("Set_C_BrenHomestead_Interior")
    base_x = 500
    
    # Room Shell
    bpy.ops.mesh.primitive_cube_add(size=1, location=(base_x, 0, 2.0))
    room = bpy.context.active_object
    room.scale = (8.0, 6.0, 4.0)
    room.name = "Homestead_Room_Shell"
    room.data.materials.append(mats['RockDark'])
    col.objects.link(room)
    bpy.context.scene.collection.objects.unlink(room)
    
    # Heavy Workbench
    bpy.ops.mesh.primitive_cube_add(size=1, location=(base_x + 2.5, 0, 1.0))
    bench = bpy.context.active_object
    bench.scale = (1.6, 4.0, 1.2)
    bench.name = "Workbench"
    bench.data.materials.append(mats['MetalRust'])
    col.objects.link(bench)
    bpy.context.scene.collection.objects.unlink(bench)
    
    # Seismograph Terminal with Glowing Screen
    bpy.ops.mesh.primitive_cube_add(size=1, location=(base_x + 2.4, 0, 1.8))
    seismo = bpy.context.active_object
    seismo.scale = (0.8, 1.4, 0.6)
    seismo.name = "Seismograph_Terminal"
    seismo.data.materials.append(mats['TurretOlive'])
    col.objects.link(seismo)
    bpy.context.scene.collection.objects.unlink(seismo)
    
    # Terminal Display Screen
    bpy.ops.mesh.primitive_cube_add(size=1, location=(base_x + 2.0, 0, 1.9))
    screen = bpy.context.active_object
    screen.scale = (0.05, 1.0, 0.4)
    screen.name = "Seismograph_Display_Glow"
    screen.data.materials.append(mats['XelNagaGlowBlue'])
    col.objects.link(screen)
    bpy.context.scene.collection.objects.unlink(screen)
    
    # Storm Shutter Window
    bpy.ops.mesh.primitive_cube_add(size=1, location=(base_x, 2.95, 2.2))
    shutter = bpy.context.active_object
    shutter.scale = (2.4, 0.1, 1.6)
    shutter.name = "Storm_Shutter_Heavy"
    shutter.data.materials.append(mats['Treads'])
    col.objects.link(shutter)
    bpy.context.scene.collection.objects.unlink(shutter)
    
    # Bunk Bed
    bpy.ops.mesh.primitive_cube_add(size=1, location=(base_x - 2.8, 1.5, 1.2))
    bunk = bpy.context.active_object
    bunk.scale = (1.8, 2.6, 2.0)
    bunk.name = "Bunk_Bed"
    bunk.data.materials.append(mats['MetalRust'])
    col.objects.link(bunk)
    bpy.context.scene.collection.objects.unlink(bunk)

def build_set_d_temple_chasm(mats):
    col = create_collection("Set_D_XelNagaTemple_Chasm")
    base_x = 850
    
    # Chasm Floor
    bpy.ops.mesh.primitive_plane_add(size=180, location=(base_x, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Chasm_Floor"
    floor.data.materials.append(mats['Mud'])
    col.objects.link(floor)
    bpy.context.scene.collection.objects.unlink(floor)
    
    # Left & Right Towering Cliff Massifs (Canyon walls)
    for side, y_off in [("NorthCliff", -65), ("SouthCliff", 65)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(base_x, y_off, 40))
        cliff = bpy.context.active_object
        cliff.scale = (160, 45, 80)
        cliff.name = f"Chasm_{side}"
        cliff.data.materials.append(mats['RockDark'])
        col.objects.link(cliff)
        bpy.context.scene.collection.objects.unlink(cliff)
        
    # The Colossal Xel'Naga Stepped Pyramid Temple (5 Tiers)
    temple_col = bpy.data.collections.new("Asset_XelNaga_Temple")
    col.children.link(temple_col)
    
    tiers = [
        (80, 80, 12, 6),
        (64, 64, 12, 18),
        (48, 48, 12, 30),
        (34, 34, 10, 41),
        (22, 22, 8, 50),
    ]
    for idx, (sx, sy, sz, cz) in enumerate(tiers):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(base_x, 0, cz))
        tier = bpy.context.active_object
        tier.scale = (sx, sy, sz)
        tier.name = f"Temple_Tier_{idx+1}"
        tier.data.materials.append(mats['XelNagaObsidian'])
        temple_col.objects.link(tier)
        bpy.context.scene.collection.objects.unlink(tier)
        
    # Glowing Geometric Energy Conduits (Lines on the tiers)
    for idx, (sx, sy, sz, cz) in enumerate(tiers):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(base_x, 0, cz + sz/2 - 0.2))
        conduit = bpy.context.active_object
        conduit.scale = (sx + 0.4, sy + 0.4, 0.4)
        conduit.name = f"Temple_Conduit_Glow_{idx+1}"
        conduit.data.materials.append(mats['XelNagaGlowBlue'])
        temple_col.objects.link(conduit)
        bpy.context.scene.collection.objects.unlink(conduit)
        
    # Triangular Gateway Portal
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=6.0, depth=2.0, location=(base_x, 40.2, 7.0))
    door = bpy.context.active_object
    door.rotation_euler = (math.radians(90), 0, 0)
    door.name = "Temple_Triangular_Portal"
    door.data.materials.append(mats['XelNagaGlowBlue'])
    temple_col.objects.link(door)
    bpy.context.scene.collection.objects.unlink(door)
    
    # The Cosmic Beacon Beam (400m vertical energy pillar)
    bpy.ops.mesh.primitive_cylinder_add(radius=4.5, depth=400.0, location=(base_x, 0, 250.0))
    beam = bpy.context.active_object
    beam.name = "Cosmic_Beacon_Pillar"
    beam.data.materials.append(mats['BeaconBeam'])
    temple_col.objects.link(beam)
    bpy.context.scene.collection.objects.unlink(beam)
    
    # Atmospheric Shockwave Rings (Torus)
    for r_idx, (r_rad, r_z) in enumerate([(25.0, 120.0), (45.0, 180.0), (70.0, 260.0)]):
        bpy.ops.mesh.primitive_torus_add(major_radius=r_rad, minor_radius=1.2, location=(base_x, 0, r_z))
        ring = bpy.context.active_object
        ring.name = f"Beacon_Shockwave_Ring_{r_idx+1}"
        ring.data.materials.append(mats['BeaconBeam'])
        temple_col.objects.link(ring)
        bpy.context.scene.collection.objects.unlink(ring)
        
    # Tiny Miniature Harvester (at base for scale)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(base_x - 30, 48, 1.2))
    mini_harv = bpy.context.active_object
    mini_harv.scale = (2.5, 4.0, 1.8)
    mini_harv.name = "Scale_Mini_RoboHarvester"
    mini_harv.data.materials.append(mats['HarvesterRed'])
    temple_col.objects.link(mini_harv)
    bpy.context.scene.collection.objects.unlink(mini_harv)
    
    # Tiny Lars Figure at the door
    bpy.ops.mesh.primitive_cube_add(size=1, location=(base_x, 38.5, 1.8))
    lars_fig = bpy.context.active_object
    lars_fig.scale = (0.5, 0.4, 1.2)
    lars_fig.name = "Figure_Lars_At_Door"
    lars_fig.data.materials.append(mats['HumanSuit'])
    temple_col.objects.link(lars_fig)
    bpy.context.scene.collection.objects.unlink(lars_fig)

def build_set_e_char(mats):
    col = create_collection("Set_E_PlanetChar_Hive")
    base_x = 1300
    
    # Cracked Basalt Floor
    bpy.ops.mesh.primitive_plane_add(size=140, location=(base_x, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Char_Basalt_Ground"
    floor.data.materials.append(mats['CharBasalt'])
    col.objects.link(floor)
    bpy.context.scene.collection.objects.unlink(floor)
    
    # Glowing Lava Fissures
    for idx, (lx, ly, rot) in enumerate([(base_x - 20, 10, 30), (base_x + 15, -25, -45), (base_x, 35, 15)]):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(lx, ly, 0.1))
        lava = bpy.context.active_object
        lava.scale = (8.0, 70.0, 0.2)
        lava.rotation_euler = (0, 0, math.radians(rot))
        lava.name = f"Char_Lava_Fissure_{idx+1}"
        lava.data.materials.append(mats['CharLava'])
        col.objects.link(lava)
        bpy.context.scene.collection.objects.unlink(lava)
        
    # Twisted Organic Zerg Spires
    for s_idx, (sx, sy, sh) in enumerate([(base_x, -10, 55), (base_x - 25, 20, 42), (base_x + 20, 15, 36)]):
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=5.0, radius2=0.5, depth=sh, location=(sx, sy, sh/2))
        spire = bpy.context.active_object
        spire.rotation_euler = (math.radians(8), math.radians(5), math.radians(45*s_idx))
        spire.name = f"Zerg_BioSpire_{s_idx+1}"
        spire.data.materials.append(mats['ZergPurple'])
        col.objects.link(spire)
        bpy.context.scene.collection.objects.unlink(spire)
        
    # Kerrigan's Bio-Throne Shelf
    bpy.ops.mesh.primitive_cube_add(size=1, location=(base_x - 5, -8, 28))
    throne = bpy.context.active_object
    throne.scale = (8.0, 6.0, 2.0)
    throne.name = "Kerrigan_BioThrone_Shelf"
    throne.data.materials.append(mats['ZergPurple'])
    col.objects.link(throne)
    bpy.context.scene.collection.objects.unlink(throne)

def setup_cameras():
    cam_col = create_collection("Cameras_Act01_Shots")
    cameras = {}
    
    # Helper to add camera
    def add_cam(name, loc, rot_deg, focal_length=35.0, clip_end=1500.0):
        cam_data = bpy.data.cameras.new(name)
        cam_data.lens = focal_length
        cam_data.clip_end = clip_end
        cam_data.display_size = 1.5
        
        cam_obj = bpy.data.objects.new(name, cam_data)
        cam_obj.location = loc
        cam_obj.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
        cam_col.objects.link(cam_obj)
        cameras[name] = cam_obj
        return cam_obj

    # 1. Shot 01: Plains wide, low ground angle looking across wheatfield toward mountains
    add_cam("Camera_Shot01_StormWide", (0, 36, 1.6), (82, 0, 180), focal_length=24.0)
    
    # 2. Shot 02: Tracking 45-degree angle behind/side harvester
    add_cam("Camera_Shot02_HarvesterTrack", (-11, 14, 4.2), (76, 0, -145), focal_length=35.0)
    
    # 3. Shot 03: Cockpit inside medium shot
    add_cam("Camera_Shot03_CockpitMS", (0, 0.2, 3.4), (90, 0, 0), focal_length=28.0)
    
    # 4. Shot 05: Free Haven perimeter, low angle looking up at missile turret & pylon
    add_cam("Camera_Shot05_TurretPerimeter", (244, 2, 2.2), (72, 0, -25), focal_length=35.0)
    
    # 5. Shot 07: Homestead interior locking the storm shutter
    add_cam("Camera_Shot07_HomesteadLock", (497.5, -2.2, 2.4), (78, 0, 30), focal_length=24.0)
    
    # 6. Shot 09: Seismograph Extreme Close Up
    add_cam("Camera_Shot09_SeismographECU", (501.2, 0, 1.95), (90, 0, -90), focal_length=70.0)
    
    # 7. Shot 12: Planet Char lava wastes & zerg spires
    add_cam("Camera_Shot12_CharHiveOverview", (1300, 65, 48), (56, 0, 180), focal_length=24.0)
    
    # 8. Shot 15: Epic high angle establishing shot of the Xel'Naga Temple in Chasm
    add_cam("Camera_Shot15_TempleChasmEpic", (850, 145, 88), (62, 0, 180), focal_length=18.0)
    
    # 9. Shot 17: Lars touching the glowing triangular portal
    add_cam("Camera_Shot17_TempleGateway", (850, 48, 4.0), (84, 0, 180), focal_length=50.0)
    
    # 10. Shot 19: Cosmic Beacon shooting 400m into stratosphere
    add_cam("Camera_Shot19_CosmicBeacon", (850, -42, 2.5), (32, 0, 0), focal_length=16.0)

    return cameras

def main():
    setup_blender()
    mats = build_materials()
    build_set_a_plains(mats)
    build_set_b_free_haven(mats)
    build_set_c_homestead(mats)
    build_set_d_temple_chasm(mats)
    build_set_e_char(mats)
    cams = setup_cameras()
    
    # Default active camera
    bpy.context.scene.camera = cams["Camera_Shot15_TempleChasmEpic"]
    
    # Save .blend file
    out_blend = r"D:\nano-video-studio\assets\storyboards\previs_act01_blocking.blend"
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print(f"SUCCESS: Saved .blend to {out_blend}")
    
    # Render preview snapshot for each camera
    render_dir = r"D:\nano-video-studio\assets\storyboards\previs_renders"
    os.makedirs(render_dir, exist_ok=True)
    
    for cam_name, cam_obj in cams.items():
        bpy.context.scene.camera = cam_obj
        out_img = os.path.join(render_dir, f"{cam_name}.png")
        bpy.context.scene.render.filepath = out_img
        bpy.ops.render.render(write_still=True)
        print(f"Rendered: {out_img}")

if __name__ == "__main__":
    main()

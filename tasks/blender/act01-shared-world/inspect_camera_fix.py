import bpy
for name in ['Cam_03_CockpitMS', 'Cam_12_CharHive']:
    obj = bpy.data.objects[name]
    print('\nCAMERA', name, 'rotation mode', obj.rotation_mode, 'constraints', [(c.name,c.type) for c in obj.constraints])
    if obj.animation_data and obj.animation_data.action:
        action = obj.animation_data.action
        try:
            curves = action.fcurves
        except AttributeError:
            curves = action.layers[0].strips[0].channelbag(obj.animation_data.action_slot).fcurves
        for fc in curves:
            print('CURVE', fc.data_path, fc.array_index, [(round(k.co.x,1),round(k.co.y,3)) for k in fc.keyframe_points][:40])
    for frame in ([145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168] if 'Cockpit' in name else [505,515,525,535,545,555,565,576]):
        bpy.context.scene.frame_set(frame)
        print('FRAME', frame, 'loc', tuple(round(x,3) for x in obj.location), 'rot',tuple(round(x,3) for x in obj.rotation_euler))

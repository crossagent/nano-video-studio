import bpy, json
s = bpy.context.scene
data = {'frame_start': s.frame_start, 'frame_end': s.frame_end, 'fps': s.render.fps,
        'collections': {}, 'markers': [], 'cameras': []}
for c in bpy.data.collections:
    data['collections'][c.name] = [{'name': o.name, 'type': o.type, 'parent': o.parent.name if o.parent else None,
                                    'location': list(o.location)} for o in c.objects]
for m in s.timeline_markers:
    data['markers'].append([m.frame, m.name, m.camera.name if m.camera else None])
for o in s.objects:
    if o.type == 'CAMERA':
        data['cameras'].append([o.name, list(o.location), o.parent.name if o.parent else None])
print('SCENE_INSPECTION=' + json.dumps(data, ensure_ascii=True))

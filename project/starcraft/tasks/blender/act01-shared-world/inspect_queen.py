import bpy
q=bpy.data.objects['Kerrigan_QueenOfBlades']
for o in q.children:
 print('CHILD',o.name,tuple(round(x,2) for x in o.location),tuple(round(x,2) for x in o.scale),o.type)

import bpy


scene = bpy.context.scene
fps = scene.render.fps / scene.render.fps_base
print(f"Scene frames {scene.frame_start}–{scene.frame_end} at {fps:g} fps")
markers = sorted(scene.timeline_markers, key=lambda marker: marker.frame)
for marker in markers:
    camera = marker.camera
    print(f"{marker.frame:3}  {marker.name}  {camera.name if camera else 'no camera'}")

for previous, following in zip(markers, markers[1:]):
    scene.frame_set(following.frame - 1)
    if scene.camera != previous.camera:
        raise RuntimeError(f"Camera mismatch before frame {following.frame}")
    scene.frame_set(following.frame)
    if scene.camera != following.camera:
        raise RuntimeError(f"Camera mismatch at frame {following.frame}")

print(f"Checked {len(markers) - 1} camera transitions")

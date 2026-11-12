import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
folder = Path(__file__).resolve().parent
graph = json.loads((root / 'tasks/comfyui/minimax-act01-wind-20261110/workflow.json').read_text(encoding='utf-8'))
graph.pop('24')
graph['5']['inputs'].pop('ref_images.ref_image_1')
graph['19']['inputs']['image'] = 'act01_s01_020_seedance_look_20261110.png'
graph['22']['inputs']['file'] = 'act01_s01_020_clay_90_20261110.mp4'
graph['23']['inputs'].update(start_frame=0, length=90)
graph['5']['inputs']['length'] = 90
graph['5']['inputs']['prompt'] = '''subject_definitions:
<Video 1> is a 24 fps clay animation defining the shot's camera, object positions and timing.
<Subject 1> is the storm-dark wet basalt rock on the muddy canyon floor. Its realistic texture and cool violet storm lighting come from <Picture 1>.

summary:
[reference generation] Generate a fully rendered realistic shot following the visual layout and action of <Video 1>, using <Picture 1> for the rock, rain, mud, lighting and atmosphere.

retention_analysis:
<Video 1> (camera, composition and motion): fully_preserved - retain the low fixed camera, rock location, lightning strike timing and fragment paths throughout the shot.
<Subject 1> (appears in [Shot 1]): attribute_transfer - the simple clay rock becomes rough dark basalt with the wet texture and storm lighting of <Picture 1>.

detailed_description:
[Shot 1] From 0.00 to 3.75 seconds, a low close shot frames the large dark basalt rock on a muddy track at the foot of a black canyon. Rain lashes sideways across wet stone and puddles. From 0.00 to 1.42 seconds the intact rock remains at the same position as in <Video 1>. At 1.42 seconds a violet-white lightning bolt strikes it. The rock fractures and fragments tumble outward in the same positions and timing as <Video 1>, settling on the road through the end of the shot. The camera remains fixed and matches <Video 1>. Every visible frame is fully rendered in realistic materials, lighting and rain; the clay geometry becomes textured stone and mud.

overall_soundscape:
Heavy wind and rain, a sharp thunder crack and rock fragments striking wet ground.
non_diegetic_music:
None.'''
graph['8']['inputs']['noise_seed'] = 2026111020
graph['9']['inputs']['steps'] = 20
graph['14']['inputs']['filename_prefix'] = 'studio/minimax-act01-rock-optimize-20261110'
(folder / 'workflow.api.json').write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding='utf-8')
batch = {'workflow': 'workflow.api.json', 'timeoutSeconds': 21600, 'jobs': [
    {'task': 'minimax-act01-rock-optimize-20261110', 'requirements': 'S01-020 雷击碎石单镜，20 步白模参考优化'}
]}
(folder / 'batch.json').write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding='utf-8')

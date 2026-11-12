import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
folder = Path(__file__).resolve().parent
base = json.loads((folder / 'workflow.api.json').read_text(encoding='utf-8'))
shots = [
    ('010', 158, 'The camera starts above a black mountain ridge, flies through the mountain pass and dives down the canyon toward the wheat field, leveling off near the wheat. The camera path, altitude, speed, and frame composition follow <Video 1> throughout the shot.', 'a black basalt canyon and a dark golden wheat field under storm clouds', 2026111030),
    ('030', 73, 'The camera is low and fixed beside the road. The same pile of broken black rocks remains on the muddy wheel track. A heavy harvester tread enters from the left, rolls over the fragments and moves to the right, keeping the contact timing and positions of <Video 1>.', 'wet black basalt debris and the tracked undercarriage of a heavy red industrial harvester', 2026111031),
    ('040', 141, 'From a low camera following the harvester on its rear right side, the heavy red tracked harvester travels toward the right. The vehicle occupies the frame and the background flows past as shown in <Video 1>. Follow its camera movement, subject scale and timing throughout.', 'a weathered red tracked industrial harvester in a stormy canyon and wheat field', 2026111032),
]
jobs = []
for shot, length, action, subject, seed in shots:
    graph = json.loads(json.dumps(base))
    graph['19']['inputs']['image'] = f'act01_s01_{shot}_seedance_look_20261110.png'
    graph['22']['inputs']['file'] = f'act01_s01_{shot}_clay_20261110.mp4'
    graph['23']['inputs'].update(start_frame=0, length=length)
    graph['5']['inputs']['length'] = length
    duration = length / 24
    graph['5']['inputs']['prompt'] = f'''subject_definitions:
<Video 1> is a 24 fps clay animation defining the camera, staging and action.
<Subject 1> is {subject}, with realistic materials and lighting from <Picture 1>.

summary:
[reference generation] Generate a fully rendered realistic shot following the visual layout and action of <Video 1>, using <Picture 1> for the appearance, materials and lighting.

retention_analysis:
<Video 1> (camera, composition and action): fully_preserved - match the original camera, object positions, subject scale and timing.
<Subject 1> (appears in [Shot 1]): attribute_transfer - the simple clay scene is rendered with the realistic appearance from <Picture 1>.

detailed_description:
[Shot 1] From 0.00 to {duration:.3f} seconds. {action} Rain, dark storm clouds and cold violet lightning illuminate the wet canyon. Every frame is fully rendered with realistic surfaces and lighting.

overall_soundscape:
Heavy wind and rain, thunder and machinery as appropriate to the action.
non_diegetic_music:
None.'''
    graph['8']['inputs']['noise_seed'] = seed
    graph['14']['inputs']['filename_prefix'] = f'studio/minimax-act01-shot{shot}-optimize-20261110'
    name = f'workflow-{shot}.api.json'
    (folder / name).write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding='utf-8')
    jobs.append((shot, name))

for shot, name in jobs:
    batch = {'workflow': name, 'timeoutSeconds': 21600, 'jobs': [
        {'task': f'minimax-act01-shot{shot}-optimize-20261110', 'requirements': f'S01-{shot} 单镜白模参考优化，20 步'}
    ]}
    (folder / f'batch-{shot}.json').write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding='utf-8')

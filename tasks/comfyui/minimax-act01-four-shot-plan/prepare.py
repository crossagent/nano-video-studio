import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
folder = Path(__file__).resolve().parent
graph = json.loads((root / 'platform/comfyui/workflows/starcraft-act01-previs-to-video.api.json').read_text(encoding='utf-8'))
graph.pop('26')
graph['5']['inputs'].pop('ref_images.ref_image_2')
graph['19']['inputs']['image'] = 'act01_minimax_canyon_wheat_20261110.jpg'
graph['24']['inputs']['image'] = 'act01_minimax_harvester_20261110.jpg'
graph['22']['inputs']['file'] = 'act01_scene01_roadside_strike_minimax_20261110.mp4'
graph['5']['inputs']['width'] = 608
graph['5']['inputs']['height'] = 256
graph['9']['inputs']['steps'] = 20
(folder / 'workflow.api.json').write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding='utf-8')

common = ('Use <Video 1> for camera movement, framing, timing, layout and actions. '
          '<Picture 1> supplies the stormy black rock and golden wheat appearance. '
          '<Picture 2> supplies the weathered red metal harvester appearance. '
          'Render as a realistic cinematic scene. Follow the video camera and action; '
          'preserve shot changes and subject positions. Violet lightning, rain, wet dark ground. ')
jobs = [
    {'task': 'minimax-act01-wind-20261110', 'requirements': 'S01-010 白模越脊俯冲', 'inputs': {
        '23': {'start_frame': 0, 'length': 144},
        '5': {'length': 141, 'prompt': common + 'The camera descends over a dark ridge, dives through the canyon and settles low over the wheat field.'},
        '8': {'noise_seed': 2026111001}, '14': {'filename_prefix': 'studio/minimax-act01-wind-20261110'}}},
    {'task': 'minimax-act01-strike-track-20261110', 'requirements': 'S01-020 至 S01-040 雷击、履带及车辆中景', 'inputs': {
        '23': {'start_frame': 144, 'length': 288},
        '5': {'length': 294, 'prompt': common + 'First show the rock close up and lightning striking and shattering it. Cut to the same debris as a harvester tread passes from left to right over it. Then cut to the harvester medium tracking shot, moving to the right.'},
        '8': {'noise_seed': 2026111002}, '14': {'filename_prefix': 'studio/minimax-act01-strike-track-20261110'}}},
]
(folder / 'batch.json').write_text(json.dumps({'workflow': 'workflow.api.json', 'jobs': jobs, 'timeoutSeconds': 21600}, ensure_ascii=False, indent=2), encoding='utf-8')

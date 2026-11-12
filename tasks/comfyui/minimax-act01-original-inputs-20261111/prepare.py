import hashlib
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[3]
folder = Path(__file__).resolve().parent
shared = Path('D:/Comfy-Desktop/ComfyUI-Shared/input')
scene = root / 'tasks/seedance/act01-scene01-whitemodel-fidelity/inputs/style-canyon-wheat.jpg'
vehicle = root / 'tasks/seedance/act01-scene01-whitemodel-fidelity/inputs/style-harvester-material-580.jpg'
source = root / 'tasks/blender/act01-scene01-previs/output/act01_scene01_roadside_strike_previs.mp4'
expected = {
    scene: '80413000d5df41b9985e815b9b48e75ad9c1f56a8401f334c71b72856c128087',
    vehicle: 'c23f535e7762b285a8d72098d5a0b9b4443efff64043c071c7c2045577689e71',
    source: '9a2202015d21ab3f8318f68e7c068b62e2b7301aa21af3a3bfc0eba156874e3a',
}
for file, digest in expected.items():
    if hashlib.sha256(file.read_bytes()).hexdigest() != digest:
        raise ValueError(f'输入摘要与记录不一致: {file}')

shutil.copyfile(scene, shared / 'original_s01_canyon_wheat_20261111.jpg')
shutil.copyfile(vehicle, shared / 'original_s01_harvester_20261111.jpg')
shots = [('010', 'minimax-act01-shot010-optimize-20261110', 's01-010-guide.mp4'),
         ('020', 'minimax-act01-rock-optimize-20261110', 's01-020-guide-90.mp4'),
         ('030', 'minimax-act01-shot030-optimize-20261110', 's01-030-guide.mp4'),
         ('040', 'minimax-act01-shot040-optimize-20261110', 's01-040-guide.mp4')]
for shot, previous, video_name in shots:
    graph = json.loads((root / 'tasks/comfyui' / previous / 'workflow.json').read_text(encoding='utf-8'))
    video = root / 'tasks/comfyui/minimax-act01-optimize-20261110/inputs' / video_name
    input_name = f'original_s01_{shot}_clay_20261111.mp4'
    shutil.copyfile(video, shared / input_name)
    graph['22']['inputs']['file'] = input_name
    graph['19']['inputs']['image'] = 'original_s01_canyon_wheat_20261111.jpg'
    graph['24'] = {'class_type': 'LoadImage', 'inputs': {'image': 'original_s01_harvester_20261111.jpg'}}
    graph['5']['inputs']['ref_images.ref_image_1'] = ['24', 0]
    prompt = graph['5']['inputs']['prompt']
    if shot in ('030', '040'):
        prompt = prompt.replace('materials and lighting from <Picture 1>', 'materials from <Picture 2> and lighting from <Picture 1>')
        prompt = prompt.replace('using <Picture 1> for the appearance, materials and lighting', 'using <Picture 1> for the environment and <Picture 2> for the harvester appearance')
        prompt = prompt.replace('realistic appearance from <Picture 1>', 'realistic scene from <Picture 1> and harvester appearance from <Picture 2>')
    prompt += ('\nReference roles: <Picture 1> supplies storm-dark canyon, golden wheat and '
               'lighting. <Picture 2> supplies weathered red industrial harvester materials. '
               'Use the camera and arrangement of <Video 1> throughout.')
    graph['5']['inputs']['prompt'] = prompt
    graph['14']['inputs']['filename_prefix'] = f'studio/minimax-original-shot{shot}-20261111'
    workflow = f'workflow-{shot}.api.json'
    (folder / workflow).write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding='utf-8')
    manifest = {'workflow': workflow, 'timeoutSeconds': 21600, 'jobs': [
        {'task': f'minimax-original-shot{shot}-20261111', 'requirements': f'S01-{shot} 原白模与 Seedance 原始参考图'}
    ]}
    (folder / f'batch-{shot}.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

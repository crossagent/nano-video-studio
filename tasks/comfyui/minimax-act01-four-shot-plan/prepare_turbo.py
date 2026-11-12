import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
folder = Path(__file__).resolve().parent
graph = json.loads((root / 'tasks/comfyui/minimax-act01-strike-track-20261110/workflow.json').read_text(encoding='utf-8'))
graph['30'] = {
    'class_type': 'LoraLoaderModelOnly',
    'inputs': {'model': ['1', 0], 'lora_name': 'minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors', 'strength_model': 1.0},
}
graph['7']['inputs']['model'] = ['30', 0]
graph['9']['inputs']['model'] = ['30', 0]
graph['9']['inputs']['steps'] = 4
graph['14']['inputs']['filename_prefix'] = 'studio/minimax-act01-strike-track-turbo-20261110'
(folder / 'workflow-turbo.api.json').write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding='utf-8')
manifest = {'workflow': 'workflow-turbo.api.json', 'timeoutSeconds': 21600, 'jobs': [
    {'task': 'minimax-act01-strike-track-turbo-20261110', 'requirements': 'S01-020 至 S01-040 雷击、履带及车辆中景，4 步加速'}
]}
(folder / 'batch-turbo.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

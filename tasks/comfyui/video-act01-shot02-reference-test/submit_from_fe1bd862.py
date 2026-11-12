import urllib.request
import json
import copy

# 1. Fetch exact working graph from fe1bd862
res = urllib.request.urlopen('http://127.0.0.1:8188/history/fe1bd862-0719-4cb6-94d9-ff7cc844d59c')
data = json.loads(res.read())
prompt_nodes = data['fe1bd862-0719-4cb6-94d9-ff7cc844d59c']['prompt'][2]

new_prompt = copy.deepcopy(prompt_nodes)

# 2. Update prompt
new_prompt["5"]["inputs"]["prompt"] = (
    "StarCraft: Shadow of the Xel'Naga, Act I, Shot 02. "
    "Camera and blocking reference: Intimate exterior low-angle tracking shot closely following the side-rear of the battered red industrial harvester. "
    "The massive vehicle dominates the left half of the frame throughout, showing its weathered red cabin, exhaust stack, and heavy caterpillar tracks as the camera overtakes smoothly along its flank through muddy wheat fields under a violent storm. "
    "<Picture 1> provides the material and environmental style reference (stormy dark violet sky, distant lightning, wind-whipped golden wheat field, industrial red paint and muddy spray). "
    "The shot composition, camera motion, and vehicle orientation MUST strictly follow the spatial blocking: vehicle on the left moving forward, camera overtaking from side-rear to side-front, no cockpit interior, no front-facing vehicle portrait. "
    "Realistic 35mm anamorphic cinematography, dark steel blue and storm violet, rain and distant lightning. No subtitles, labels, watermarks, diagrams, UI or reference-sheet layout."
)

# 3. Update ControlNet parameters: strength 0.75, end_percent 0.85
new_prompt["48"]["inputs"]["strength"] = 0.75
new_prompt["48"]["inputs"]["start_percent"] = 0.0
new_prompt["48"]["inputs"]["end_percent"] = 0.85

# 4. Update inputs to use v2 calibrated 5s depth and previs
new_prompt["102"]["inputs"]["video"] = r"D:\Comfy-Desktop\ComfyUI-Shared\input\StarCraft_Shot02_TrueDepth_5s_v2.mp4"
new_prompt["103"]["inputs"]["video"] = r"D:\Comfy-Desktop\ComfyUI-Shared\input\StarCraft_Shot02_Previs_5s_v2.mp4"

# 5. Update save prefix
new_prompt["14"]["inputs"]["filename_prefix"] = "studio/StarCraft_Act01_Shot02_CloseupDepth_StrongControl"

# 6. Post prompt
req_data = json.dumps({"prompt": new_prompt}).encode('utf-8')
req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=req_data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as resp:
        res_json = json.loads(resp.read().decode('utf-8'))
        prompt_id = res_json.get("prompt_id")
        print("Prompt submitted successfully!")
        print("New Prompt ID:", prompt_id)
        with open(r"D:\nano-video-studio\tasks\comfyui\video-act01-shot02-reference-test\latest_prompt_id.txt", "w") as f:
            f.write(prompt_id)
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)

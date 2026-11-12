import urllib.request
import json
import av

# 1. Load exact working graph from the latest successful MP4 run
c = av.open(r"D:\Comfy-Desktop\ComfyUI-Shared\output\studio\StarCraft_Act01_Shot02_CloseupDepth_StrongControl_00001_.mp4")
prompt = json.loads(c.metadata["prompt"])

# 2. Industry-standard semantic slot-filling prompt
prompt_text = (
    "StarCraft: Shadow of the Xel'Naga, Act I, Shot 02. "
    "Camera motion and spatial reference: Strictly follow the camera trajectory, framing, and spatial blocking of <Video 1>. "
    "Intimate exterior low-angle tracking shot closely following the side-rear of the vehicle as it races forward, "
    "with the camera smoothly overtaking along its left flank. "
    "Replace the red and dark blockout vehicle body in <Video 1> with the battered industrial robo-harvester from <Picture 1> "
    "(weathered crimson red paint, heavy caterpillar treads, exhaust stacks, muddy spray). "
    "Replace the ground in <Video 1> with the storm-swept golden wheat field from <Picture 1>. "
    "Realistic 35mm anamorphic cinematography, dark steel blue and storm violet sky, distant lightning. "
    "Continuous tracking shot, strictly maintain the side-rear overtaking motion, no camera cuts, no front portrait."
)

prompt["5"]["inputs"]["prompt"] = prompt_text

# 3. Completely unplug ControlNet: connect UNET directly to BasicGuider and BasicScheduler
prompt["7"]["inputs"]["model"] = ["1", 0]
prompt["9"]["inputs"]["model"] = ["1", 0]

# Remove ControlNet and depth-related nodes
for nid in ["48", "50", "102", "98:92"]:
    if nid in prompt:
        del prompt[nid]

# 4. Ensure ref_video_0 is our 5s calibrated RGB previs
prompt["103"]["inputs"]["video"] = r"D:\Comfy-Desktop\ComfyUI-Shared\input\StarCraft_Shot02_Previs_5s_v2.mp4"
prompt["5"]["inputs"]["ref_videos.ref_video_0"] = ["103", 0]
prompt["5"]["inputs"]["ref_images.ref_image_0"] = ["26", 0]

# 5. Set seed and save prefix
prompt["8"]["inputs"]["noise_seed"] = 2026110601
prompt["14"]["inputs"]["filename_prefix"] = "studio/StarCraft_Act01_Shot02_PurePrevis_NoControlNet"

# 6. Post prompt
req_data = json.dumps({"prompt": prompt}).encode('utf-8')
req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=req_data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as resp:
        res_json = json.loads(resp.read().decode('utf-8'))
        prompt_id = res_json.get("prompt_id")
        print("Prompt submitted successfully without ControlNet!")
        print("Prompt ID:", prompt_id)
        with open(r"D:\nano-video-studio\tasks\comfyui\video-act01-shot02-reference-test\latest_prompt_id.txt", "w") as f:
            f.write(prompt_id)
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode('utf-8'))
except Exception as e:
    print("Error submitting prompt:", e)

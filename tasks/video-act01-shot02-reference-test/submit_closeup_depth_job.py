import urllib.request
import json
import os

prompt_dict = {
  "1": {
    "inputs": {
      "unet_name": "minimax_h3_ref2va_pruned_int8_convrot.safetensors",
      "weight_dtype": "default"
    },
    "class_type": "UNETLoader"
  },
  "2": {
    "inputs": {
      "clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
      "type": "minimax",
      "device": "default"
    },
    "class_type": "CLIPLoader"
  },
  "3": {
    "inputs": {
      "vae_name": "minimax_h3_video_vae_int8_convrot.safetensors"
    },
    "class_type": "VAELoader"
  },
  "4": {
    "inputs": {
      "vae_name": "minimax_h3_audio_vae_fp32.safetensors"
    },
    "class_type": "VAELoader"
  },
  "5": {
    "inputs": {
      "prompt": "StarCraft: Shadow of the Xel'Naga, Act I, Shot 02. Camera and blocking reference: Intimate exterior low-angle tracking shot closely following the side-rear of the battered red industrial harvester. The massive vehicle dominates the left half of the frame, showing its weathered red cabin, exhaust stack, and heavy caterpillar tracks as the camera overtakes smoothly along its flank through muddy wheat fields under a violent storm. <Picture 1> provides the material and environmental style reference (stormy dark violet sky, distant lightning, wind-whipped golden wheat field, industrial red paint and muddy spray). The shot composition, camera motion, and vehicle orientation MUST strictly follow the spatial blocking: vehicle on the left moving forward, camera overtaking from side-rear to side-front, no cockpit interior, no front-facing vehicle portrait.",
      "width": 768,
      "height": 320,
      "length": 124,
      "ref_image_size": "match",
      "clip": ["2", 0],
      "vae": ["3", 0],
      "audio_vae": ["4", 0],
      "ref_images.ref_image_0": ["26", 0],
      "ref_videos.ref_video_0": ["103", 0]
    },
    "class_type": "MiniMaxH3ReferenceToVideo"
  },
  "6": {
    "inputs": {
      "sampler_name": "res_multistep"
    },
    "class_type": "KSamplerSelect"
  },
  "7": {
    "inputs": {
      "model": ["48", 0],
      "conditioning": ["5", 0]
    },
    "class_type": "BasicGuider"
  },
  "8": {
    "inputs": {
      "seed": 2026110412
    },
    "class_type": "RandomNoise"
  },
  "9": {
    "inputs": {
      "scheduler": "beta",
      "steps": 20,
      "denoise": 1.0,
      "model": ["1", 0]
    },
    "class_type": "BasicScheduler"
  },
  "10": {
    "inputs": {
      "noise": ["8", 0],
      "guider": ["7", 0],
      "sampler": ["6", 0],
      "sigmas": ["9", 0],
      "latent_image": ["5", 1]
    },
    "class_type": "SamplerCustomAdvanced"
  },
  "11": {
    "inputs": {
      "samples": ["10", 0],
      "vae": ["3", 0]
    },
    "class_type": "VAEDecode"
  },
  "12": {
    "inputs": {
      "images": ["11", 0],
      "frame_rate": 24,
      "loop_count": 0,
      "filename_prefix": "studio/StarCraft_Act01_Shot02_CloseupDepth_StrongControl",
      "format": "video/h264-mp4",
      "pix_fmt": "yuv420p",
      "crf": 19,
      "save_output": True
    },
    "class_type": "VHS_VideoCombine"
  },
  "26": {
    "inputs": {
      "image": "scene-01-bhekar-ro-wheatfield-storm.png"
    },
    "class_type": "LoadImage"
  },
  "48": {
    "inputs": {
      "strength": 0.75,
      "start_percent": 0.0,
      "end_percent": 0.85,
      "model": ["1", 0],
      "model_patch": ["50", 0],
      "vae": ["3", 0],
      "control_video": ["102", 0]
    },
    "class_type": "MiniMaxH3FunControlNetApply"
  },
  "50": {
    "inputs": {
      "name": "minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors"
    },
    "class_type": "ModelPatchLoader"
  },
  "102": {
    "inputs": {
      "video": r"D:\Comfy-Desktop\ComfyUI-Shared\input\StarCraft_Shot02_TrueDepth_5s_v2.mp4",
      "force_rate": 0.0,
      "custom_width": 0,
      "custom_height": 0,
      "frame_load_cap": 0,
      "skip_first_frames": 0,
      "select_every_nth": 1,
      "format": "AnimateDiff"
    },
    "class_type": "VHS_LoadVideoPath"
  },
  "103": {
    "inputs": {
      "video": r"D:\Comfy-Desktop\ComfyUI-Shared\input\StarCraft_Shot02_Previs_5s_v2.mp4",
      "force_rate": 0.0,
      "custom_width": 0,
      "custom_height": 0,
      "frame_load_cap": 0,
      "skip_first_frames": 0,
      "select_every_nth": 1,
      "format": "AnimateDiff"
    },
    "class_type": "VHS_LoadVideoPath"
  }
}

req_data = json.dumps({"prompt": prompt_dict}).encode('utf-8')
req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=req_data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("Prompt submitted successfully!")
        print("Prompt ID:", res.get("prompt_id"))
        with open(r"D:\nano-video-studio\tasks\video-act01-shot02-reference-test\latest_prompt_id.txt", "w") as f:
            f.write(res.get("prompt_id"))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode('utf-8'))
except Exception as e:
    print("Error submitting prompt:", e)

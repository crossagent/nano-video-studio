import os
import cv2
import numpy as np

output_dir = r"C:\Users\zhouxy\.gemini\antigravity\brain\8a8b1a5d-37b3-41a0-9766-7d40d49fda25\eval_pure_previs"
os.makedirs(output_dir, exist_ok=True)

previs_path = r"D:\Comfy-Desktop\ComfyUI-Shared\input\StarCraft_Shot02_Previs_5s_v2.mp4"
control_strong_path = r"D:\Comfy-Desktop\ComfyUI-Shared\output\studio\StarCraft_Act01_Shot02_CloseupDepth_StrongControl_00001_.mp4"
pure_previs_path = r"D:\Comfy-Desktop\ComfyUI-Shared\output\studio\StarCraft_Act01_Shot02_PurePrevis_NoControlNet_00001_.mp4"

def get_frames(video_path, frame_indices):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = {}
    for idx in frame_indices:
        target = min(idx - 1, total_frames - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, target))
        ret, frame = cap.read()
        if ret:
            frames[idx] = frame
        else:
            frames[idx] = np.zeros((320, 768, 3), dtype=np.uint8)
    cap.release()
    return frames, total_frames, fps

frame_indices = [1, 31, 62, 93, 124]

print("Extracting frames from Previs...")
previs_frames, p_total, p_fps = get_frames(previs_path, frame_indices)

print("Extracting frames from ControlNet Strong...")
control_frames, c_total, c_fps = get_frames(control_strong_path, frame_indices)

print("Extracting frames from Pure Previs (No ControlNet)...")
pure_frames, pure_total, pure_fps = get_frames(pure_previs_path, frame_indices)

# Save individual generated frames
for idx in frame_indices:
    frame = pure_frames[idx]
    save_path = os.path.join(output_dir, f"pure_f{idx:03d}.jpg")
    cv2.imwrite(save_path, frame)
    print(f"Saved: {save_path}")

# Build 3-way contact sheet
# Row 1: Blender 3D Previs
# Row 2: ControlNet Strong 0.75
# Row 3: Native Reference-To-Video (No ControlNet)
target_w = 400
target_h = int(target_w * 320 / 768)

rows = []
labels = [
    "[1] Blender 3D Previs (Ground Truth Tracking)",
    "[2] ControlNet Depth Strong 0.75 (Previous Test)",
    "[3] Native Reference-To-Video (No ControlNet, Current Test)"
]

for label, source_dict in zip(labels, [previs_frames, control_frames, pure_frames]):
    row_imgs = []
    for idx in frame_indices:
        img = source_dict[idx].copy()
        img = cv2.resize(img, (target_w, target_h))
        # Add frame stamp
        cv2.putText(img, f"F{idx:03d}", (10, target_h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)
        row_imgs.append(img)
    combined_row = np.hstack(row_imgs)

    # Add title banner above row
    banner = np.zeros((30, combined_row.shape[1], 3), dtype=np.uint8)
    cv2.putText(banner, label, (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    rows.append(np.vstack([banner, combined_row]))

contact_sheet = np.vstack(rows)
contact_path = os.path.join(output_dir, "contact_sheet_3way_pure_previs.jpg")
cv2.imwrite(contact_path, contact_sheet)
print(f"Contact sheet saved to: {contact_path}")

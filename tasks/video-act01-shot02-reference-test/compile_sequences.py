import cv2
import os
import shutil
import numpy as np

depth_dir = r"D:\nano-video-studio\tasks\video-act01-shot02-reference-test\depth_frames"
previs_dir = r"D:\nano-video-studio\tasks\video-act01-shot02-reference-test\previs_frames"
out_dir = r"D:\nano-video-studio\tasks\video-act01-shot02-reference-test"
shared_dir = r"D:\Comfy-Desktop\ComfyUI-Shared\input"

depth_mp4 = os.path.join(out_dir, "StarCraft_Shot02_TrueDepth_5s_v2.mp4")
previs_mp4 = os.path.join(out_dir, "StarCraft_Shot02_Previs_5s_v2.mp4")

# Check frames
frames = [f"frame_{i:04d}.png" for i in range(1, 125)]
assert all(os.path.exists(os.path.join(depth_dir, f)) for f in frames), "Missing depth frames"
assert all(os.path.exists(os.path.join(previs_dir, f)) for f in frames), "Missing previs frames"

# Compile depth MP4
first_img = cv2.imread(os.path.join(depth_dir, frames[0]))
h, w, _ = first_img.shape
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

out_depth = cv2.VideoWriter(depth_mp4, fourcc, 24.0, (w, h))
for f in frames:
    img = cv2.imread(os.path.join(depth_dir, f))
    out_depth.write(img)
out_depth.release()
print(f"Compiled {depth_mp4} ({os.path.getsize(depth_mp4)} bytes)")

# Compile previs MP4
out_previs = cv2.VideoWriter(previs_mp4, fourcc, 24.0, (w, h))
for f in frames:
    img = cv2.imread(os.path.join(previs_dir, f))
    out_previs.write(img)
out_previs.release()
print(f"Compiled {previs_mp4} ({os.path.getsize(previs_mp4)} bytes)")

# Copy to shared input
shutil.copy2(depth_mp4, os.path.join(shared_dir, "StarCraft_Shot02_TrueDepth_5s_v2.mp4"))
shutil.copy2(previs_mp4, os.path.join(shared_dir, "StarCraft_Shot02_Previs_5s_v2.mp4"))
print("Copied both MP4s to ComfyUI shared input folder.")

# Build 5-frame contact sheet comparing RGB and Depth
sample_indices = [1, 31, 62, 93, 124]
rows = []
for idx in sample_indices:
    fn = f"frame_{idx:04d}.png"
    p_img = cv2.imread(os.path.join(previs_dir, fn))
    d_img = cv2.imread(os.path.join(depth_dir, fn))
    # Add labels
    cv2.putText(p_img, f"Previs RGB Frame {idx}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(d_img, f"True Depth Frame {idx}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    combined = np.hstack([p_img, d_img])
    rows.append(combined)

sheet = np.vstack(rows)
contact_sheet_path = os.path.join(out_dir, "contact_sheet_closeup_v2.jpg")
cv2.imwrite(contact_sheet_path, sheet)
print(f"Saved contact sheet to {contact_sheet_path}")

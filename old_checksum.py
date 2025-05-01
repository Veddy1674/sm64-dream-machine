import cv2
import numpy as np
import os, shutil

# difference between 1 and 2, 3 and 4, 5 and 6 and so on is 0.0
# so instead of capturing and updating with emu.atvi, we just remove duplicates
# so that the frames are 30 fps and there are less inputs to save

### CHECKSUM
# img1 = cv2.imread("frames/frame_00005.png")
# img2 = cv2.imread("frames/frame_00006.png")

# diff = cv2.absdiff(img1, img2)
# print("avg pixel difference:", np.mean(diff))

### CONVERT TO 30 FPS
frame_folder = "preframes"
filtered_folder = "frames"

if os.path.exists(filtered_folder):
    shutil.rmtree(filtered_folder) # empty
os.makedirs(filtered_folder, exist_ok=True)
print("Emptied/Created output folder")

threshold = 1.0 # also skip really similar frames, for this reason "checksum.py" is used instead

frame_files = sorted([f for f in os.listdir(frame_folder) if f.endswith(".png")])
kept = 0

for i in range(0, len(frame_files) - 1, 2):
    file1 = os.path.join(frame_folder, frame_files[i])
    file2 = os.path.join(frame_folder, frame_files[i + 1])

    img1 = cv2.imread(file1)
    img2 = cv2.imread(file2)

    diff = cv2.absdiff(img1, img2)
    avg_diff = np.mean(diff)

    # debug
    print(f"frame {i} vs {i+1} - avg diff: {avg_diff:.2f}")
    
    if avg_diff > threshold:
        dst_path = os.path.join(filtered_folder, f"frame_{kept:05d}.png")
        shutil.copy(file1, dst_path)
        kept += 1

print(f"\nKept {kept} frames out of {len(frame_files)}")
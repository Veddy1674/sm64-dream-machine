# aviToPng.py

import os, shutil
import cv2

video_folder = r"C:\Users\anton\Downloads\mario\v2\videos\whomp1\videos"
output_folder = r"C:\Users\anton\Downloads\mario\v2\videos\whomp1\preframes"

if os.path.exists(output_folder):
    shutil.rmtree(output_folder) # empty
os.makedirs(output_folder, exist_ok=True)
print("Emptied/Created output folder")

top_crop = 20
bottom_crop = 20

resize_dim = (96, 96)

# find .avi files
avi_files = sorted([f for f in os.listdir(video_folder) if f.endswith(".avi")])

frame_count = 0
for video_file in avi_files:
    video_path = os.path.join(video_folder, video_file)
    cap = cv2.VideoCapture(video_path)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # cut black borders (20 pixel wide)
        cropped = frame[top_crop:frame.shape[0] - bottom_crop, :]
        
        # change size to 96x96
        resized = cv2.resize(cropped, resize_dim, interpolation=cv2.INTER_AREA)
        
        # save
        frame_filename = f"frame_{frame_count:05d}.png"
        cv2.imwrite(os.path.join(output_folder, frame_filename), resized)
        frame_count += 1

    cap.release()

print(f"Saved {frame_count} frames")
import os, shutil

src_folder = "preframes"
dst_folder = "frames"

if os.path.exists(dst_folder):
    shutil.rmtree(dst_folder) # empty
os.makedirs(dst_folder, exist_ok=True)
print("Emptied/Created output folder")

frame_files = sorted([f for f in os.listdir(src_folder) if f.endswith(".png")])

kept = 0
for i, fname in enumerate(frame_files):
    if i % 2 == 0: # only if even
        src = os.path.join(src_folder, fname)
        dst = os.path.join(dst_folder, f"frame_{kept:05d}.png")
        shutil.copy(src, dst)
        kept += 1

print(f"Kept {kept} frames out of {len(frame_files)}")
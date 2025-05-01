import os
import random
import torch
import cv2
import numpy as np
from torchvision import transforms
from train_model import DreamNet

device = "cuda" if torch.cuda.is_available() else "cpu"
frames_dir = "frames"
output_dir = "output"
model_path = "dreamnet.pth"

os.makedirs(output_dir, exist_ok=True)

transform = transforms.Compose([
    transforms.ToTensor(),
])
to_pil = transforms.ToPILImage()

model = DreamNet().to(device)
model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()

all_frames = sorted(os.listdir(frames_dir))
idx = random.randint(0, len(all_frames) - 2)
frame_path = os.path.join(frames_dir, all_frames[idx])
img = cv2.imread(frame_path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
cv2.imwrite(os.path.join(output_dir, "target.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR)) # save target.png

tensor_img = transform(img).unsqueeze(0).to(device)

actions = {
    "up":     [1, 0, 0, 0],
    "down":   [0, 1, 0, 0],
    "left":   [0, 0, 1, 0],
    "right":  [0, 0, 0, 1],
}

for name, act in actions.items():
    input_tensor = torch.tensor([act], dtype=torch.float32).to(device)
    with torch.no_grad():
        output = model(tensor_img, input_tensor).squeeze(0).cpu()
    out_img = to_pil(output)
    out_img.save(os.path.join(output_dir, f"{name}.png"))

print(f"Predictions saved in '{output_dir}' from frame {idx} ({all_frames[idx]})")

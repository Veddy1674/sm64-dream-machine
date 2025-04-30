# predict_dream.py

import torch
from PIL import Image
from torchvision import transforms
from train_dream import DreamNet
import os
import random

DEVICE = 'cpu'
IMAGE_SIZE = 96
SEQ_LEN = 4
TOTAL_FRAMES = 10

transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
])

def load_images(frame_paths):
    imgs = []
    for p in frame_paths:
        img = Image.open(p).convert('RGB')
        imgs.append(transform(img))
    return torch.stack(imgs)

def tensor_checksum(tensor):
    return torch.sum(tensor).item()

def save_tensor(tensor, path):
    img = transforms.ToPILImage()(tensor.squeeze(0))
    img.save(path)

def generate_sequence():
    model = DreamNet().to(DEVICE)
    model.load_state_dict(torch.load('data/dreamnet_epoch35.pt', map_location=DEVICE))
    model.eval()

    all_frames = sorted(os.listdir("frames"), key=lambda x: int(x.replace("frame_", "").split(".")[0]))
    start = random.randint(0, len(all_frames) - SEQ_LEN - TOTAL_FRAMES)
    paths = [os.path.join("frames", all_frames[start + i]) for i in range(SEQ_LEN)]
    sequence = load_images(paths).unsqueeze(0).to(DEVICE)

    os.makedirs("output/generated", exist_ok=True)

    for i in range(SEQ_LEN):
        save_tensor(sequence[0, i], f"output/generated/frame_{i:03d}.png")

    current_seq = sequence.clone()

    for i in range(TOTAL_FRAMES):
        inp = current_seq.view(-1, SEQ_LEN * 3, IMAGE_SIZE, IMAGE_SIZE) # model must be nn.Conv2d(SEQ_LEN * 3, 64, 4, 2, 1)
        with torch.no_grad():
            pred = model(inp)

        save_tensor(pred, f"output/generated/frame_{i + SEQ_LEN:03d}.png")

        pred = pred.unsqueeze(1)
        current_seq = torch.cat([current_seq[:, 1:], pred], dim=1)

        print(f"frame {i + SEQ_LEN} predicted")

generate_sequence()
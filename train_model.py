import os
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
from tqdm import tqdm

frames_dir = "frames"
inputs_file = "videos/inputs.txt"
image_size = 96
epochs = 25
batch_size = 16
sequence_len = 5
device = "cuda" if torch.cuda.is_available() else "cpu"
model_path = "dreamnet.pth"

class MarioDataset(torch.utils.data.Dataset):
    def __init__(self, frames_dir, inputs_file, transform=None):
        self.frames = sorted(os.listdir(frames_dir))
        self.inputs = [list(map(int, line.strip().split(','))) for line in open(inputs_file).readlines()]
        self.transform = transform

    def __len__(self):
        return len(self.frames) - sequence_len

    def __getitem__(self, idx):
        imgs, inps = [], []
        for i in range(sequence_len):
            img = cv2.imread(os.path.join(frames_dir, self.frames[idx + i]))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            if self.transform:
                img = self.transform(img)
            imgs.append(img)
            inps.append(torch.tensor(self.inputs[idx + i], dtype=torch.float32))
        target = cv2.imread(os.path.join(frames_dir, self.frames[idx + sequence_len]))
        target = cv2.cvtColor(target, cv2.COLOR_BGR2RGB)
        if self.transform:
            target = self.transform(target)
        return imgs, inps, target

class DreamNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 32, 4, 2, 1), nn.ReLU(),
            nn.Conv2d(32, 64, 4, 2, 1), nn.ReLU(),
            nn.Conv2d(64, 128, 4, 2, 1), nn.ReLU(),
        )
        self.fc_input = nn.Linear(4, 128)
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 4, 2, 1), nn.ReLU(),
            nn.ConvTranspose2d(128, 64, 4, 2, 1), nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 4, 2, 1), nn.ReLU(),
            nn.Conv2d(32, 3, 3, 1, 1), nn.Sigmoid()
        )

    def forward(self, x, action):
        z = self.encoder(x)
        a = self.fc_input(action).view(-1, 128, 1, 1).expand(-1, 128, z.shape[2], z.shape[3])
        combined = torch.cat([z, a], dim=1)
        return self.decoder(combined)

transform = transforms.Compose([
    transforms.ToTensor(),
])

dataset = MarioDataset(frames_dir, inputs_file, transform)
loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

model = DreamNet().to(device)

if os.path.exists(model_path):
    print(f"[INFO] Found existing model '{model_path}', loading weights...")
    model.load_state_dict(torch.load(model_path, map_location=device))
else:
    print(f"[INFO] No existing model found. Training a new one from scratch.")

optimizer = optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()

if __name__ == "__main__":
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for img_seq, action_seq, target in tqdm(loader, desc=f"Epoch {epoch+1}/{epochs}"):
            prev = img_seq[0].to(device)
            for i in range(1, sequence_len):
                optimizer.zero_grad()
                act = action_seq[i - 1].to(device)
                pred = model(prev, act)
                prev = pred.detach()
            target = target.to(device)
            act = action_seq[-1].to(device)
            final_pred = model(prev, act)
            loss = loss_fn(final_pred, target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(loader)
        print(f"[EPOCH {epoch+1}/{epochs}] Loss: {avg_loss:.6f}")

    torch.save(model.state_dict(), model_path)
    print(f"[INFO] Model saved to '{model_path}'")

# train_dream.py

import os
import torch
import torchvision.transforms as T
from torch.utils.data import Dataset, DataLoader
from torchvision.utils import save_image
from PIL import Image
from tqdm import tqdm
import torch.nn as nn

# param
IMAGE_SIZE = 96 # 96x96 (no black borders)
SEQ_LEN = 4 # from SEQ_LEN frames, predict the next
BATCH_SIZE = 8
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# transforming
transform = T.Compose([
    T.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    T.ToTensor(),
])

# dataset
class FrameDataset(Dataset):
    def __init__(self, folder):
        self.folder = folder
        self.paths = sorted(os.listdir(folder), key=lambda x: int(x.replace('frame_', '').split('.')[0]))

    def __len__(self):
        return len(self.paths) - SEQ_LEN

    def __getitem__(self, idx):
        imgs = []
        for i in range(SEQ_LEN + 1):
            path = os.path.join(self.folder, self.paths[idx + i])
            img = Image.open(path).convert('RGB') #!
            imgs.append(transform(img))
        return torch.stack(imgs[:-1]), imgs[-1]

# cnn
class DreamNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(SEQ_LEN * 3, 64, 4, 2, 1),
            nn.ReLU(),
            nn.Conv2d(64, 128, 4, 2, 1),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 4, 2, 1),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 3, 4, 2, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x

def train():
    dataset = FrameDataset("frames")
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    model = DreamNet().to(DEVICE)
    optim = torch.optim.Adam(model.parameters(), lr=1e-4)
    loss_fn = nn.MSELoss()

    for epoch in range(10): # debug
        pbar = tqdm(loader)
        for seq, target in pbar:
            seq = seq.to(DEVICE)
            target = target.to(DEVICE)
            inp = seq.view(-1, SEQ_LEN * 3, IMAGE_SIZE, IMAGE_SIZE)
            pred = model(inp)
            loss = loss_fn(pred, target)
            optim.zero_grad()
            loss.backward()
            optim.step()
            pbar.set_description(f"Epoch {epoch+1}, Loss: {loss.item():.4f}")
        os.makedirs("data", exist_ok=True) # save in data/
        os.makedirs("output", exist_ok=True)
        torch.save(model.state_dict(), f'data/dreamnet_epoch{epoch+1}.pt')
        save_image(pred[0], f'output/predicted_{epoch+1}.png')
        save_image(target[0], f'output/target_{epoch+1}.png')

if __name__ == '__main__':
    train()
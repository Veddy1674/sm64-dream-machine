import os
import cv2
import torch
import numpy as np
import keyboard
from torchvision import transforms
from train_model import DreamNet

model_path = "dreamnet.pth"
frames_dir = "frames"
device = "cuda" if torch.cuda.is_available() else "cpu"

# load model
model = DreamNet().to(device)
model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()

# transforming
transform = transforms.Compose([transforms.ToTensor()])
to_pil = transforms.ToPILImage()

first_frame = cv2.imread(os.path.join(frames_dir, "frame_00000.png"))
first_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB)
tensor_frame = transform(first_frame).unsqueeze(0).to(device)

# setup window
cv2.namedWindow("Predicted", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Predicted", 384, 384)

print("Controls: W (up), A (left), S (right), D (down), SPACE (idle), ESC (exit)")

while True:
    key = cv2.waitKey(1)

    # keylistening
    action = [0, 0, 0, 0]
    if keyboard.is_pressed("w"):
        action = [1, 0, 0, 0]
    elif keyboard.is_pressed("d"):
        action = [0, 1, 0, 0]
    elif keyboard.is_pressed("a"):
        action = [0, 0, 1, 0]
    elif keyboard.is_pressed("s"):
        action = [0, 0, 0, 1]
    elif keyboard.is_pressed("space"):
        action = [0, 0, 0, 0]
    elif keyboard.is_pressed("r"): # reset to first image
        tensor_frame = transform(first_frame).unsqueeze(0).to(device)
    elif keyboard.is_pressed("esc"):
        print("Exiting...")
        cv2.destroyAllWindows()
        break
    else:
        continue  # no input

    # predict
    input_tensor = torch.tensor([action], dtype=torch.float32).to(device)
    with torch.no_grad():
        output = model(tensor_frame, input_tensor).squeeze(0).cpu()

    # show
    out_img = to_pil(output)
    out_bgr = cv2.cvtColor(np.array(out_img), cv2.COLOR_RGB2BGR)
    cv2.imshow("Predicted", out_bgr)

    # use prediction as input
    tensor_frame = transform(np.array(out_img)).unsqueeze(0).to(device)

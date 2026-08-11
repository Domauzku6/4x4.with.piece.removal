import torch

model = torch.load("game_ai_model.pth", map_location="cpu")
print(model)  # test
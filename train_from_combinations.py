import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import os
import ast
from tqdm import tqdm

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device} 🚀")


# --- 1. GAME WIN CHECKER ---
def check_win(board, someone):
    for row in range(4):
        if np.all(board[row, :] == someone): return True
    for col in range(4):
        if np.all(board[:, col] == someone): return True
    if np.all(np.diag(board) == someone): return True
    if np.all(np.diag(np.fliplr(board)) == someone): return True
    if board[0, 0] == someone and board[0, 3] == someone and board[3, 0] == someone and board[3, 3] == someone:
        return True
    return False


# --- 2. NEURAL NETWORK ARCHITECTURE ---
class GameAI(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(16, 128)
        self.fc2 = nn.Linear(128, 128)
        self.policy_head = nn.Linear(128, 16)
        self.value_head = nn.Linear(128, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        policy = F.softmax(self.policy_head(x), dim=-1)
        value = torch.tanh(self.value_head(x))
        return policy, value


# --- 3. STREAMING DATASET & TRAINING ---
def train_from_file(file_path="combinations.txt", epochs=5, batch_size=256):
    model = GameAI().to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    if os.path.exists("game_ai_model.pth"):
        print("Loading existing model weights...")
        state = torch.load("game_ai_model.pth", map_location=device)
        model.load_state_dict({k.replace("_orig_mod.", ""): v for k, v in state.items()}, strict=False)

    print(f"🚀 Training model from '{file_path}'...")

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        batches_processed = 0

        # Count total lines for progress bar
        print(f"\n--- Epoch {epoch + 1}/{epochs} ---")
        with open(file_path, "r") as f:
            total_lines = sum(1 for _ in f)

        state_buffer = []
        value_buffer = []

        with open(file_path, "r") as f:
            pbar = tqdm(f, total=total_lines, desc=f"Training Epoch {epoch + 1}", unit="board")
            for line in pbar:
                board_list = ast.literal_eval(line.strip())
                board = np.array(board_list, dtype=np.float32)

                # Determine value based on terminal game state
                flat_board = board.reshape(4, 4)
                if check_win(flat_board, 1):
                    val = 1.0
                elif check_win(flat_board, 2):
                    val = -1.0
                else:
                    val = 0.0  # Neutral or intermediate position

                net_board = np.where(flat_board == 1, 1.0, np.where(flat_board == 2, -1.0, 0.0)).flatten()

                state_buffer.append(net_board)
                value_buffer.append(val)

                if len(state_buffer) >= batch_size:
                    b_states = torch.tensor(np.array(state_buffer), dtype=torch.float32, device=device)
                    b_vals = torch.tensor(np.array(value_buffer), dtype=torch.float32, device=device).unsqueeze(1)

                    optimizer.zero_grad()
                    _, pred_vals = model(b_states)
                    loss = criterion(pred_vals, b_vals)
                    loss.backward()
                    optimizer.step()

                    total_loss += loss.item()
                    batches_processed += 1
                    pbar.set_postfix(Loss=f"{loss.item():.4f}")

                    state_buffer.clear()
                    value_buffer.clear()

            # Process remaining buffer
            if state_buffer:
                b_states = torch.tensor(np.array(state_buffer), dtype=torch.float32, device=device)
                b_vals = torch.tensor(np.array(value_buffer), dtype=torch.float32, device=device).unsqueeze(1)
                optimizer.zero_grad()
                _, pred_vals = model(b_states)
                loss = criterion(pred_vals, b_vals)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
                batches_processed += 1

        avg_loss = total_loss / max(1, batches_processed)
        print(f"Epoch {epoch + 1} Completed | Average Loss: {avg_loss:.5f}")

    torch.save(model.state_dict(), "game_ai_model.pth")
    print("\n💾 Trained model successfully saved to 'game_ai_model.pth'!")


if __name__ == "__main__":
    train_from_file()
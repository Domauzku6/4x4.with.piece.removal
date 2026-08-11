import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import os
import math


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


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = GameAI().to(device)

if os.path.exists("game_ai_model.pth"):
    state = torch.load("game_ai_model.pth", map_location=device)
    model.load_state_dict({k.replace("_orig_mod.", ""): v for k, v in state.items()}, strict=False)
model.eval()


def check_win_sim(board, someone):
    for row in range(4):
        if np.all(board[row, :] == someone): return True
    for col in range(4):
        if np.all(board[:, col] == someone): return True
    if np.all(np.diag(board) == someone): return True
    if np.all(np.diag(np.fliplr(board)) == someone): return True
    if board[0, 0] == someone and board[0, 3] == someone and board[3, 0] == someone and board[3, 3] == someone:
        return True
    return False


class MCTSNode:
    def __init__(self, board, parent=None, prior=0.0):
        self.board = board.copy()
        self.parent = parent
        self.children = {}
        self.visit_count = 0
        self.value_sum = 0.0
        self.prior = prior

    def q_value(self):
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count


def ai_place(board, bot_id=2, player_id=1):
    empty = [(r, c) for r in range(4) for c in range(4) if board[r, c] == 0]
    if not empty:
        return None

    # Immediate win/block check for absolute safety
    for (r, c) in empty:
        board[r, c] = bot_id
        if check_win_sim(board, bot_id):
            board[r, c] = 0
            return r, c
        board[r, c] = 0
    for (r, c) in empty:
        board[r, c] = player_id
        if check_win_sim(board, player_id):
            board[r, c] = 0
            return r, c
        board[r, c] = 0

    root = MCTSNode(board)

    # Run MCTS simulations guided by the Neural Network (DeepMind style)
    num_simulations = 100
    for _ in range(num_simulations):
        node = root
        sim_board = board.copy()

        # 1. Selection
        while node.children:
            # UCB1 formula combined with neural network prior probabilities
            best_score = -float('inf')
            best_action = None
            best_child = None

            for action, child in node.children.items():
                u_score = child.q_value() + 1.41 * child.prior * math.sqrt(node.visit_count + 1) / (
                            1 + child.visit_count)
                if u_score > best_score:
                    best_score = u_score
                    best_action = action
                    best_child = child

            node = best_child
            r, c = divmod(best_action, 4)
            sim_board[r, c] = bot_id if np.sum(sim_board == bot_id) == np.sum(sim_board == player_id) else player_id

        # Check terminal state in simulation
        if check_win_sim(sim_board, bot_id):
            value = 1.0
        elif check_win_sim(sim_board, player_id):
            value = -1.0
        else:
            # 2. Expansion & Evaluation using Neural Network
            net_board = np.where(sim_board == bot_id, 1.0, np.where(sim_board == player_id, -1.0, 0.0)).astype(
                np.float32)
            flat = net_board.flatten()

            with torch.no_grad():
                policy, val = model(torch.from_numpy(flat).unsqueeze(0).to(device))
                policy = policy.squeeze(0).cpu().numpy()
                value = val.item()

            sim_empty = [(r, c) for r in range(4) for c in range(4) if sim_board[r, c] == 0]
            for (r, c) in sim_empty:
                action_idx = r * 4 + c
                next_b = sim_board.copy()
                next_b[r, c] = bot_id
                node.children[action_idx] = MCTSNode(next_b, parent=node, prior=policy[action_idx])

        # 3. Backpropagation
        curr = node
        while curr is not None:
            curr.visit_count += 1
            curr.value_sum += value
            curr = curr.parent
            value = -value  # Switch perspective for opponent

    # Choose the most visited action from the root
    best_action = max(root.children, key=lambda a: root.children[a].visit_count)
    return divmod(best_action, 4)
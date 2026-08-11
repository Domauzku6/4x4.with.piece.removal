import numpy as np
from tqdm import tqdm


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


def generate_and_save_boards(output_file="combinations.txt", save_every=500000):
    print("Generating reachable board combinations iteratively with disk streaming...")

    queue = [np.zeros((4, 4), dtype=int)]
    visited = {tuple(np.zeros(16, dtype=int))}

    total_saved = 0
    buffer = []

    pbar = tqdm(desc="Discovering Boards", unit=" states")

    with open(output_file, "w") as f:
        while queue:
            board = queue.pop(0)
            buffer.append(str(board.tolist()) + "\n")
            pbar.update(1)

            # Periodically flush buffer to disk to save RAM
            if len(buffer) >= save_every:
                f.writelines(buffer)
                total_saved += len(buffer)
                buffer.clear()

            p1_count = np.sum(board == 1)
            p2_count = np.sum(board == 2)

            if check_win(board, 1) or check_win(board, 2) or (p1_count + p2_count == 16):
                continue

            next_player = 1 if p1_count == p2_count else 2
            empty_spaces = np.where(board == 0)

            for r, c in zip(empty_spaces[0], empty_spaces[1]):
                next_board = board.copy()
                next_board[r, c] = next_player

                p1_next = np.sum(next_board == 1)
                p2_next = np.sum(next_board == 2)
                if abs(p1_next - p2_next) > 1:
                    continue

                state_tuple = tuple(next_board.flatten())
                if state_tuple not in visited:
                    visited.add(state_tuple)
                    queue.append(next_board)

        # Write any remaining items in the buffer
        if buffer:
            f.writelines(buffer)
            total_saved += len(buffer)

    pbar.close()
    print(f"\n✨ Done! Total unique board states saved: {total_saved}")
    print(f"💾 Safely stored in '{output_file}' without overloading RAM.")


if __name__ == "__main__":
    generate_and_save_boards()
import numpy as np
import math

# --- ORIGINAL GAME LOGIC ---[cite: 2]

game_board = np.full((4, 4), 0)
player = 1
bot = 2
max_piece_count = 4
player_piece_count = 0
player_moves = []
bot_piece_count = 0
bot_moves = []


def place_bot(x, y):
    global game_board, bot_piece_count, bot_moves
    if game_board[x, y] == 0:
        bot_piece_count += 1
        bot_moves.append((x, y))
        game_board[x, y] = bot
        return game_board
    else:
        return False


def place_player(x, y):
    global game_board, player_piece_count, player_moves
    if game_board[x, y] == 0:
        player_piece_count += 1
        player_moves.append((x, y))
        game_board[x, y] = player
        return game_board
    else:
        return False


def player_removal_test():
    global game_board, player_piece_count, player_moves, max_piece_count
    if player_piece_count > max_piece_count:
        player_piece_count -= 1
        first_move_x, first_move_y = player_moves.pop(0)
        game_board[first_move_x, first_move_y] = 0
        return game_board
    else:
        return game_board


def bot_removal_test():
    global game_board, bot_piece_count, bot_moves, max_piece_count
    if bot_piece_count > max_piece_count:
        bot_piece_count -= 1
        first_move_x, first_move_y = bot_moves.pop(0)
        game_board[first_move_x, first_move_y] = 0
        return game_board
    else:
        return game_board


def check_win_dont_use(someone):
    global game_board

    for row in range(4):
        if np.all(game_board[row, :] == someone):
            return True

    for col in range(4):
        if np.all(game_board[:, col] == someone):
            return True

    if np.all(np.diag(game_board) == someone):
        return True

    if np.all(np.diag(np.fliplr(game_board)) == someone):
        return True

    return False


def game_win():
    global player, game_board, bot
    if check_win_dont_use(player):
        print("Player wins!")
        return True
    else:
        if check_win_dont_use(bot):
            print("Bot wins!")
            return True
        else:
            return False


# --- MINIMAX & SIMULATION ADDITIONS ---

def simulate_move(current_board, current_moves, player_type, x, y):
    """Safely simulates a move and piece removal without altering the real game."""
    sim_board = np.copy(current_board)
    sim_moves = list(current_moves)

    if sim_board[x, y] != 0:
        return None, None

    sim_board[x, y] = player_type
    sim_moves.append((x, y))

    if len(sim_moves) > 4:
        oldest_x, oldest_y = sim_moves.pop(0)
        sim_board[oldest_x, oldest_y] = 0

    return sim_board, sim_moves


def check_win_sim(board_state, someone):
    """A copy of your win checker that works on simulated boards instead of the global board."""
    for row in range(4):
        if np.all(board_state[row, :] == someone): return True
    for col in range(4):
        if np.all(board_state[:, col] == someone): return True
    if np.all(np.diag(board_state) == someone): return True
    if np.all(np.diag(np.fliplr(board_state)) == someone): return True
    return False


def get_empty_spaces(board_state):
    """Returns a list of all (x, y) coordinates that are currently 0."""
    spaces = []
    for r in range(4):
        for c in range(4):
            if board_state[r, c] == 0:
                spaces.append((r, c))
    return spaces


def minimax(sim_board, depth, alpha, beta, is_maximizing, current_bot_moves, current_player_moves):
    """The recursive Minimax algorithm with Alpha-Beta pruning."""
    # 1. Base Cases: Win/Loss
    if check_win_sim(sim_board, bot):
        return 1000 + depth  # Bot wants to win as fast as possible
    if check_win_sim(sim_board, player):
        return -1000 - depth  # Bot wants to delay losing as long as possible

    # 2. Depth limit reached
    if depth == 0 or len(get_empty_spaces(sim_board)) == 0:
        return 0  # Neutral score

    empty_spaces = get_empty_spaces(sim_board)

    # 3. Maximizing (Bot's turn)
    if is_maximizing:
        max_eval = -math.inf
        for (x, y) in empty_spaces:
            new_board, new_bot_moves = simulate_move(sim_board, current_bot_moves, bot, x, y)
            eval_score = minimax(new_board, depth - 1, alpha, beta, False, new_bot_moves, current_player_moves)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Prune branch
        return max_eval

    # 4. Minimizing (Player's turn)
    else:
        min_eval = math.inf
        for (x, y) in empty_spaces:
            new_board, new_player_moves = simulate_move(sim_board, current_player_moves, player, x, y)
            eval_score = minimax(new_board, depth - 1, alpha, beta, True, current_bot_moves, new_player_moves)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Prune branch
        return min_eval


def get_best_bot_move():
    """Starts the Minimax calculation for the current real board and returns the best coordinates."""
    best_score = -math.inf
    best_move = None
    empty_spaces = get_empty_spaces(game_board)

    depth_limit = 4  # Looks ahead 2 of your turns and 2 of the bot's turns

    for (x, y) in empty_spaces:
        # Simulate the first move
        new_board, new_bot_moves = simulate_move(game_board, bot_moves, bot, x, y)

        # Trigger minimax for the opponent's response
        score = minimax(new_board, depth_limit - 1, -math.inf, math.inf, False, new_bot_moves, player_moves)

        if score > best_score:
            best_score = score
            best_move = (x, y)

    # Fallback to the first available space if everything is perfectly tied
    if best_move is None and empty_spaces:
        best_move = empty_spaces[0]

    return best_move
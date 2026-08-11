import numpy as np

game_board = np.full((4, 4), 0)
player = 1
bot = 2


def place_piece(user, x, y):
    global game_board
    game_board[x, y] = user
    return game_board


def check_win(someone):
    global game_board
    for row in range(4):
        if np.all(game_board[row, :] == someone): return True
    for col in range(4):
        if np.all(game_board[:, col] == someone): return True
    if np.all(np.diag(game_board) == someone): return True
    if np.all(np.diag(np.fliplr(game_board)) == someone): return True

    # Kampai (Corners) Win
    if (game_board[0, 0] == someone and game_board[0, 3] == someone and
            game_board[3, 0] == someone and game_board[3, 3] == someone):
        return True
    return False


def game_win():
    global player, bot
    if check_win(player):
        print("Player wins!")
        return True
    elif check_win(bot):
        print("Bot wins!")
        return True
    return False


def get_empty_spaces():
    global game_board
    spaces = []
    for r in range(4):
        for c in range(4):
            if game_board[r, c] == 0:
                spaces.append((r, c))
    return spaces
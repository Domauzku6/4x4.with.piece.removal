import numpy as np

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
    if game_board[x,y] == 0:
        player_piece_count +=1
        player_moves.append((x, y))
        game_board[x, y] = player
        return game_board
    else:
        return False


def player_removal():
    global game_board, player_piece_count, player_moves, max_piece_count
    if player_piece_count > max_piece_count:
        player_piece_count -= 1
        first_move_x, first_move_y = player_moves.pop(0)
        game_board[first_move_x, first_move_y] = 0
        return game_board
    else:
        return game_board
def bot_removal():
    global game_board, bot_piece_count, bot_moves, max_piece_count
    if bot_piece_count > max_piece_count:
        bot_piece_count -= 1
        first_move_x, first_move_y = bot_moves.pop(0)
        game_board[first_move_x, first_move_y] = 0
        return game_board
    else:
        return game_board

def check_win(someone):
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

    # if none false
    return False

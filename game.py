import game_core_functions as game_core_functions

player = 1
bot = 2
print("no cubes, 3x3 rules every time you place piece 4 piece on next turn 5 piece will be removed")

while not game_core_functions.game_win():
    print(game_core_functions.game_board)

    while True:
        x, y = map(int, input("player move x, y: ").split(","))
        if not (0 <= x <= 3 and 0 <= y <= 3):
            print("Invalid move! Coordinates must be between 0 and 3.")
            continue
        if game_core_functions.game_board[x, y] > 0:
            print("space not empty")
            continue
        else:
            break

    game_core_functions.place_player(x, y)
    game_core_functions.player_removal_test()

    if game_core_functions.game_win():
        print(game_core_functions.game_board)
        break

    print(game_core_functions.game_board)


    while True:
        x, y = map(int, input("bot move x, y: ").split(","))
        if not (0 <= x <= 3 and 0 <= y <= 3):
            print("Invalid move! Coordinates must be between 0 and 3.")
            continue
        if game_core_functions.game_board[x, y] > 0:
            print("space not empty")
            continue
        else:
            break

    game_core_functions.place_bot(x, y)
    game_core_functions.bot_removal_test()

    if game_core_functions.game_win():
        print(game_core_functions.game_board)
        break
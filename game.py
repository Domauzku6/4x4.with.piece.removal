import game_core_functions as game_core_functions
player = 1
bot = 2
print("no cubes, 3x3 rules every time you place piece 4 piece on next turn 5 piece will be removed")
while not game_core_functions.game_win():
    print(game_core_functions.game_board)
    x, y = map(int, input("player move x, y").split(","))
    game_core_functions.place_player(x,y)
    game_core_functions.game_win()
    game_core_functions.player_removal_test()
    print(game_core_functions.game_board)
    x, y = map(int, input("bot move x,y").split(","))
    game_core_functions.place_bot(x, y)
    game_core_functions.game_win()
    game_core_functions.bot_removal_test()


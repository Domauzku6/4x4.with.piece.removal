import game_core_functions as gcf
from game_core_functions import player, bot
from ai import ai_place

print("4x4 Game: Connect 4 in a row, column, diagonal, or 4 corners to win!")

while not gcf.game_win():
    print(gcf.game_board)

    if not gcf.get_empty_spaces():
        print("Draw!")
        break

    while True:
        try:
            x, y = map(int, input("player move x, y: ").split(","))
            if 0 <= x <= 3 and 0 <= y <= 3 and gcf.game_board[x, y] == 0:
                break
            print("Invalid or taken space.")
        except ValueError:
            print("Use format x,y (e.g. 1,2)")

    gcf.place_piece(player, x, y)
    if gcf.game_win():
        print(gcf.game_board)
        break

    print(gcf.game_board)
    print("Bot is thinking...")
    bx, by = ai_place(gcf.game_board, bot, player)
    print(f"Bot chooses: {bx},{by}")

    gcf.place_piece(bot, bx, by)
    if gcf.game_win():
        print(gcf.game_board)
        break
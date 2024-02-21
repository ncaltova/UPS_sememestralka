from sys import argv
import game.game as game


if __name__ == '__main__':
    connect_info = None

    if len(argv) == 3:
        connect_info = argv[1:]

    game = game.Game()
    game.game_loop(connect_info)

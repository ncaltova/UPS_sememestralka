import pygame

import connection.components
import connection.connection
import game.game_room as game_room
import game.join_screen as join_screen
import game.menu as menu
import game.wait_room as wait_room
import game.winner_screen as winner_screen


class Game:
    def __init__(self):
        self.__window = self.window_init()
        self.__location = 'menu'
        self.__running = True
        self.__clock = pygame.time.Clock()
        self.__conn = connection.connection.Connection()
        self.__this_player = None
        self.__current_game_state = None
        self.__connect_info = None
        self.__menu = menu.Menu(self.__window, self.end_application, self.join_game)
        self.__join_menu = join_screen.JoinScreen(self.__window, self.back_home, self.connect_submit)
        self.__wait_room = wait_room.WaitRoom(self.__window, self.disconnect)
        self.__game_room = None  # init az po prvnim game_state
        self.__winner_screen = winner_screen.WinnerScreen(self.__window, self.connect_again, self.back_home)

    def window_init(self):
        pygame.init()
        pygame.display.set_caption('Mau-Mau - Card game')
        pygame_icon = pygame.image.load('img/logo.png')
        pygame.display.set_icon(pygame_icon)
        return pygame.display.set_mode((800, 600), pygame.RESIZABLE)

    def end_application(self):
        if self.__location == 'wait_room':
            self.__conn.leave_game()
            self.__conn.exit()

        self.__running = False

    def join_game(self):
        self.__menu.validation.text_string = ''
        self.__location = 'join_game'

    def connect_again(self):
        self.connect_to_wait_room(None, None)

    def connect_submit(self):
        if self.__connect_info is not None:
            self.join_game()
            self.connect_to_wait_room(self.__connect_info[0], self.__connect_info[1])
        else:
            self.connect_to_wait_room(
                self.__join_menu.form.address_input.input_text.text_string,
                self.__join_menu.form.username_input.input_text.text_string
            )

    def connect_to_wait_room(self, server_address, player_name):
        if server_address is not None and player_name is not None:
            if ':' not in server_address:
                self.__join_menu.validation.text_string = 'Invalid address'
                return

            address = server_address.split(':')

            if not self.__conn.validate_and_connect(address[0], int(address[1])):
                self.__join_menu.validation.text_string = 'Could not connect to server'
                return

            handshake = self.__conn.handshake()
            if handshake == self.__conn.err or handshake == self.__conn.net_err or handshake == self.__conn.timeout_err:
                self.__join_menu.validation.text_string = 'Could not connect to server'
                self.__conn.conn.close()
                return

        join_game = self.__conn.join_game(None)

        if join_game == self.__conn.validation_err:
            return

        if join_game == self.__conn.err or join_game == self.__conn.timeout_err:
            self.__join_menu.validation.text_string = 'Could not join game'
            self.__conn.conn.close()
            return

        elif join_game == self.__conn.net_err:
            self.__menu.validation.text_string = 'Lost connection to the server'
            self.__location = 'menu'
            self.__conn.conn.close()
            return

        self.__this_player = connection.components.Player(player_name)
        self.__this_player.player_id = join_game

        self.__join_menu.validation.text_string = ''
        self.__location = 'wait_room'

    def get_game_info(self):
        game_state = self.__conn.get_game_state(self.__this_player)

        if game_state == self.__conn.timeout_err:
            return
        elif game_state == self.__conn.net_err or game_state == self.__conn.err:
            self.__menu.validation.text_string = 'Lost connection to the server'
            self.__location = 'menu'
            self.__conn.conn.close()
            return

        player_deck = self.__conn.get_player_deck()

        if player_deck == self.__conn.timeout_err:
            return
        elif player_deck == self.__conn.net_err or player_deck == self.__conn.err:
            self.__menu.validation.text_string = 'Lost connection to the server'
            self.__location = 'menu'
            self.__conn.conn.close()
            return

        return connection.components.GameInfo(game_state, player_deck)

    def ping_server(self):
        is_alive = self.__conn.is_alive()
        if is_alive == self.__conn.err or is_alive == self.__conn.net_err:
            self.__menu.validation.text_string = 'Lost connection to the server'
            self.__location = 'menu'
            self.__conn.conn.close()

    def back_home(self):
        self.__location = 'menu'

    def disconnect(self):
        self.__conn.leave_game()
        self.__conn.exit()
        self.__location = 'menu'

    def get_game_end(self):
        winner_id = self.__conn.get_game_end()

        if self.__this_player.player_id == winner_id:
            return self.__this_player

        for player in self.__current_game_state.players:
            if player.player_id == winner_id:
                return player

    def change_type(self, placed_card):
        change_type = self.__game_room.get_change_type()

        if placed_card is not None and placed_card.value == 'top' and change_type is not None:
            self.__game_room.hide_change_type()
            response = self.__conn.make_move(placed_card, change_type, self.__this_player.player_id)

            if response is None:
                self.__this_player.cards.remove(placed_card)
                self.__game_room.update_this_player(self.__this_player)
                return
            elif isinstance(response, str) and response == "ace":
                return
            elif isinstance(response, list):
                self.__this_player.cards.extend(response)
                self.__game_room.update_this_player(self.__this_player)
                return

    def make_move(self):
        placed_card = None
        drawn = None

        if placed_card is None and drawn is None:
            placed_card = self.__game_room.place_card()
            drawn = self.__game_room.draw_card()

            if placed_card is not None and placed_card.value == 'top':
                return placed_card

        if placed_card is not None and placed_card.value != 'top':
            response = self.__conn.make_move(placed_card, None, self.__this_player.player_id)

            if response is None:
                self.__this_player.cards.remove(placed_card)
                self.__game_room.update_this_player(self.__this_player)
                return
            elif isinstance(response, str) and response == "ace":
                return
            elif isinstance(response, list):
                self.__this_player.cards.extend(response)
                self.__game_room.update_this_player(self.__this_player)
                return

        elif drawn is not None:
            response = self.__conn.make_move(None, None, self.__this_player.player_id)

            if isinstance(response, str) and response == "ace":
                return
            elif isinstance(response, list):
                self.__this_player.cards.extend(response)
                self.__game_room.update_this_player(self.__this_player)
                return

    def game_loop(self, connect_info=None):
        loop_index = 1
        placed_card = None

        if connect_info is not None:
            self.__connect_info = connect_info

        while self.__running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.end_application()
                elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                    self.end_application()
                elif self.__location == 'menu' and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.__menu.check_events()
                elif self.__location == 'join_game' and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.__join_menu.check_inputs()
                    self.__join_menu.check_buttons()
                elif self.__location == 'join_game' and event.type == pygame.KEYDOWN:
                    self.__join_menu.input_text(event)
                elif self.__location == 'wait_room' and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.__wait_room.check_button()
                elif self.__location == 'game' and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.__current_game_state.current_player.player_id == self.__this_player.player_id:
                        placed_card = self.make_move()
                        if placed_card is not None:
                            self.__game_room.show_change_type()
                            self.__location = 'change'
                elif self.__location == 'change' and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.__current_game_state.current_player.player_id == self.__this_player.player_id and placed_card is not None:
                        self.change_type(placed_card)

                    self.__game_room.hide_change_type()
                    self.__location = 'game'
                elif self.__location == 'winner_screen' and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.__winner_screen.check_button()


            if self.__location == 'menu':
                self.__menu.draw()
            elif self.__location == 'join_game':
                self.__join_menu.draw()
            elif self.__location == 'wait_room':
                self.__wait_room.draw()
                if self.__conn.conn is not None and (loop_index % 40) == 0:
                    loop_index = 1
                    game_info = self.get_game_info()
                    if game_info is not None:
                        self.__location = 'game'
                        self.__this_player.cards = game_info.deck
                        self.__current_game_state = game_info.game_state
                        self.__game_room = game_room.GameRoom(self.__window, game_info.game_state, self.__this_player)
                    elif game_info is None and self.__location == 'game':
                        self.__winner_screen.update_winner_text(f'no one')
                        self.__location = 'winner_screen'

            elif self.__location == 'game' or self.__location == 'change':
                winner = None

                for player in self.__current_game_state.players:
                    if player.cards_count == 0 or len(self.__this_player.cards) == 0:
                        winner = self.__conn.get_game_end()
                        if self.__this_player.player_id == winner:
                            self.__winner_screen.update_winner_text(self.__this_player.username)
                        else:
                            self.__winner_screen.update_winner_text(f'Opponent {winner}')
                        self.__location = 'winner_screen'

                if winner is None:
                    if self.__conn.conn is not None and (loop_index % 40) == 0:
                        loop_index = 1
                        game_info = self.get_game_info()

                        if game_info is not None:
                            self.__game_room.update_game_state(game_info.game_state, self.__this_player)
                            self.__current_game_state = game_info.game_state
                            self.__this_player.cards = game_info.deck
                        elif game_info is None and self.__location == 'game':
                            self.__winner_screen.update_winner_text(f'no one')
                            self.__location = 'winner_screen'

                    if self.__current_game_state.current_type == "":
                        self.__game_room.draw(self.__current_game_state.top_card.type)
                    else:
                        self.__game_room.draw(self.__current_game_state.current_type)
            elif self.__location == 'winner_screen':
                self.__winner_screen.draw()

            loop_index += 1
            pygame.display.flip()
            self.__clock.tick(15)

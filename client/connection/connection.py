import inspect
import re
import socket

import connection.components as components


class Connection:
    def __init__(self):
        self.conn = None
        self.max_length = 4096
        self.err = -1
        self.net_err = -2
        self.timeout_err = -3
        self.validation_err = -4

    def receive(self, response_regex):
        try:
            data = self.conn.recv(self.max_length).decode()
        except:
            return None, self.err

        status = 0

        if re.search(response_regex, data) is None:
            if 'status_code=300' in data:
                status = self.timeout_err
            else:
                print(data)
                status = self.err

        print(f"[recieve|{inspect.stack()[1].function}] recieved data: {data}")

        return data, status

    def validate_and_connect(self, address, port):
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((address, port))
            return True
        except socket.error:
            return False

    def handshake(self):
        try:
            self.conn.send('request_type=handshake\n'.encode())
            _, status = self.receive("^(response_type=handshake&status_code=200)")

            if status:
                return status
        except ConnectionResetError:
            return self.net_err
        except socket.timeout:
            return self.timeout_err

    def join_game(self, player_id):

        try:
            if player_id is not None:
                self.conn.send(f'request_type=join_game?player_id={player_id}\n'.encode())
                response, status = self.receive("^(response_type=join_game&status_code=200)")
            else:
                self.conn.send(f'request_type=join_game\n'.encode())
                response, status = self.receive("^(response_type=join_game&status_code=200&player_id=\d)")

            if status:
                return status

            # Returns player_id
            if player_id is None:
                return int(response.split('&')[2].split('=')[1].strip('\n'))

        except ConnectionResetError:
            return self.net_err
        except socket.timeout:
            return self.timeout_err
        except:
            return self.err

    def leave_game(self):
        try:
            self.conn.send(f'request_type=leave_game\n'.encode())

            _, status = self.receive("^(response_type=join_game&status_code=200)")

            if status:
                return status

        except ConnectionResetError:
            return self.net_err
        except socket.timeout:
            return self.timeout_err

    def exit(self):
        try:
            self.conn.send(f'request_type=exit\n'.encode())

            _, status = self.receive("^(response_type=exit&status_code=200)")

            if status:
                return status

            self.conn.close()

        except ConnectionResetError:
            return self.net_err
        except socket.timeout:
            return self.timeout_err

    def is_alive(self):
        try:
            self.conn.send(f'request_type=is_alive\n'.encode())
            _, status = self.receive("^(response_type=is_alive&status_code=200)")

            if status:
                return status

        except ConnectionResetError:
            return self.net_err
        except socket.timeout:
            return self.timeout_err

    def make_move(self, card, change_type, player_id):
        try:
            if change_type is not None and card is not None:
                self.conn.send(
                    f'request_type=move_finish?player_id={player_id}&card=[card_type={card.type}&'
                    f'card_value={card.value}&change={change_type}]\n'.encode())
            elif card is not None:
                print( f'request_type=move_finish?player_id={player_id}&card=[card_type={card.type}&'
                    f'card_value={card.value}]\n')
                self.conn.send(
                    f'request_type=move_finish?player_id={player_id}&card=[card_type={card.type}&'
                    f'card_value={card.value}]\n'.encode())
            else:
                self.conn.send(
                    f'request_type=move_finish?player_id={player_id}\n'.encode())

            response, status = self.receive("^response_type=move_finish&status_code=200&(cards=(?:nil|\[card_type=["
                                            "^&]+&card_value=[^&]+(?:;card_type=[^&]+&card_value=[^&]+)*\])|card=\["
                                            "card_type=[^&]+&card_value=[^&]+\])&type=(?:ace|seven|place|draw)$")

            if status:
                return status

            move_type = response.split('&type')[1].replace('=', '').replace('\n', '')

            if move_type == 'ace':
                return "ace"
            elif move_type == 'place':
                return None
            elif move_type == 'seven':
                return self.draw_two(response)
            elif move_type == 'draw':
                return self.draw_card(response)
            else:
                return self.err

        except ConnectionResetError:
            return self.net_err
        except socket.timeout:
            return self.timeout_err

    def draw_card(self, response):
        drawn_card = response.split('card=[')[1].split(']')[0].split('&')

        return [components.Card(drawn_card[0].split('=')[1], drawn_card[1].split('=')[1])]

    def draw_two(self, response):

        drawn_cards = response.split('cards=[')[1].split(']')[0].split(';')
        card1 = drawn_cards[0].split('&')
        card2 = drawn_cards[1].split('&')

        return [components.Card(card1[0].split('=')[1], card1[1].split('=')[1]),
                components.Card(card2[0].split('=')[1], card2[1].split('=')[1])]

    def get_game_state(self, this_player):
        try:
            self.conn.send('request_type=game_state\n'.encode())
            data, status = self.receive("^response_type=game_state&status_code=\d+&current_player_id=\d+&players=\[("
                                        "?:player_id=\d+&count=\d+&is_active=("
                                        "?:true|false);)*player_id=\d+&count=\d+&is_active=("
                                        "?:true|false)\]&top_card=\[card_type=\w+&card_value=\w+\]&current_type=\w*$")

            if status:
                return status

            return self.parse_game_state(data, this_player)

        except ConnectionResetError:
            return self.net_err
        except socket.timeout:
            return self.timeout_err

    def get_player_deck(self):
        try:
            self.conn.send('request_type=player_deck\n'.encode())
            data, status = self.receive("^response_type=player_deck&status_code=200&cards=((\[(?:card_type=["
                                        "^&;]+&card_value=[^&;]+;?)+\])|nil)$")

            if status:
                return status

            return self.get_deck_init(data)

        except ConnectionResetError:
            return self.net_err
        except socket.timeout:
            return self.timeout_err

    def parse_game_state(self, response, this_player):
        response_cards = response.split('top_card=[')[1].replace(']', '').split('&')
        new_game_state = components.GameState(None, [], components.Card(response_cards[0].split('=')[1],
                                                                        response_cards[1].split('=')[1]),
                                              response_cards[2].split('=')[1].replace('\n', ''))

        curr_player = int(response.split('&')[2].split('=')[1])

        response_players = response.split('players=[')[1].split(']')[0].split(';')

        for player in response_players:
            split = player.split('&')
            temp = components.Opponent(int(split[0].split('=')[1]), int(split[1].split('=')[1]),
                                       bool(split[2].split('=')[1]))

            new_game_state.players.append(temp)

            if curr_player == temp.player_id:
                new_game_state.current_player = temp

        if new_game_state.current_player is None:
            new_game_state.current_player = this_player

        return new_game_state

    def get_deck_init(self, response):
        new_deck = []
        if 'cards=[' in response:
            for card in response.split('cards=[')[1].split(']')[0].split(';'):
                card_parts = card.split('&')
                new_deck.append(components.Card(card_parts[0].split('=')[1], card_parts[1].split('=')[1]))

        return new_deck

    def get_game_end(self):
        try:
            self.conn.send('request_type=game_end\n'.encode())
            data, status = self.receive("^response_type=game_end&status_code=200&winner=\d+$")

            if status:
                return status

            return int(data.split('&')[2].split('=')[1].split("\n")[0])

        except ConnectionResetError:
            return self.net_err
        except socket.timeout:
            return self.timeout_err

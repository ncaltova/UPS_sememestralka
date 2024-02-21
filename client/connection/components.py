class Player:
    def __init__(self, username):
        self.player_id = None
        self.username = username
        self.cards = None
        self.active = True


class Opponent:
    def __init__(self, player_id, cards_count, active):
        self.player_id = player_id
        self.cards_count = cards_count
        self.active = active


class Card:
    def __init__(self, card_type, value):
        self.type = card_type
        self.value = value

    def __eq__(self, other):
        if self.type == other.type and self.value == other.value:
            return True
        else:
            return False


class GameState:
    def __init__(self, current_player, players, top_card, current_type):
        self.current_player = current_player
        self.players = players
        self.top_card = top_card
        self.current_type = current_type


class GameInfo:
    def __init__(self, game_state, deck):
        self.game_state = game_state
        self.deck = deck

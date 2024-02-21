import game.components


class GameRoom:
    def __init__(self, surface, game_state, this_player):
        self.__this_player = this_player
        self.__surface = surface
        self.__game_state = game_state
        self.__card_deck = game.components.CardDeck(0, 0, self.__game_state.top_card)
        self.__player_deck = game.components.PlayerDeck(self.__this_player.cards, self.__this_player.username,
                                                        0, 0)
        self.__opponents = game.components.Opponents(game_state.players, 0, 0)
        self.__current_player = game.components.CurrentPlayer('', 0, 0)
        self.__current_player.update_label(game_state.current_player, self.__this_player.player_id)
        self.__change_type = game.components.ChangeType("img/change_type.png", 0, 0)
        self.__current_type = game.components.CurrentType(0, 0)

    def show_change_type(self):
        self.__change_type.is_visible = True

    def hide_change_type(self):
        self.__change_type.is_visible = False

    def get_change_type(self):
        return self.__change_type.check_buttons()

    def place_card(self):
        return self.__player_deck.place_card()

    def draw_card(self):
        return self.__card_deck.draw_card()

    def update_this_player(self, this_player):
        self.__player_deck.update_cards(this_player.cards)

    def update_game_state(self, game_state, this_player):
        self.__game_state = game_state
        self.__player_deck.update_cards(this_player.cards)
        self.__card_deck.top_card.update_card(self.__game_state.top_card)
        self.__opponents.update_opponents(game_state.players)
        self.__current_player.update_label(game_state.current_player, self.__this_player.player_id)

    def draw(self, curr_type):
        self.__surface.fill((255, 249, 224))

        self.__card_deck.rect.x = (self.__surface.get_width() / 2) - (self.__card_deck.rect.width / 2)
        self.__card_deck.rect.y = (self.__surface.get_height() / 2) - (self.__card_deck.rect.height / 2)

        self.__player_deck.y = self.__surface.get_height()

        self.__opponents.x = 25

        self.__current_player.x = self.__surface.get_width()
        self.__current_player.y = (self.__surface.get_height() / 2)

        self.__change_type.rect.x = (self.__surface.get_width() / 2) - (self.__change_type.rect.width / 2)
        self.__change_type.rect.y = 20

        self.__current_type.x = self.__surface.get_width() - 20
        self.__current_type.y = 20

        self.__card_deck.draw(self.__surface)
        self.__player_deck.draw(self.__surface)
        self.__opponents.draw(self.__surface)
        self.__current_player.draw(self.__surface)
        self.__change_type.draw(self.__surface)
        self.__current_type.draw(self.__surface, curr_type)

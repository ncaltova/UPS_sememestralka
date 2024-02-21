import pygame
import connection.components


class Button:
    def __init__(self, x, y, image, on_click):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.on_click = on_click

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def click(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            self.on_click()


class Text:
    def __init__(self, x, y, text, font, size, color):
        self.x = x
        self.y = y
        self.text_string = text
        self.font = pygame.font.Font(font, size)
        self.color = color
        self.text = self.font.render(text, True, self.color)

    def draw(self, screen):
        self.text = self.font.render(self.text_string, True, self.color)
        screen.blit(self.text, (self.x, self.y))


class Input:
    def __init__(self, label, background_image, background_image_active, x, y):
        self.input_text = Text(0, 0, "", 'fonts/PixelifySans-Regular.ttf', 16, (0, 0, 0))
        self.is_active = False
        self.label = Text(0, 0, label, 'fonts/PixelifySans-Regular.ttf', 31, (0, 0, 0))
        self.background_image = background_image
        self.background_image_active = background_image_active
        self.rect = pygame.rect.Rect(0, 0, background_image.get_rect().width + self.label.text.get_rect().width,
                                     background_image.get_rect().height + self.label.text.get_rect().height)
        self.rect.topleft = (x, y)

    def set_active(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            self.is_active = True
        else:
            self.is_active = False

    def input(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.input_text.text_string = self.input_text.text_string[:-1]
        else:
            if len(self.input_text.text_string) < 20:
                self.input_text.text_string += event.unicode

    def draw(self, surface):

        self.label.x = self.rect.x
        self.label.y = self.rect.y
        self.label.draw(surface)

        if not self.is_active:
            surface.blit(self.background_image, (self.rect.x + self.label.text.get_width(), self.rect.y))
        else:
            surface.blit(self.background_image_active, (self.rect.x + self.label.text.get_width(), self.rect.y))

        self.input_text.x = self.rect.x + self.label.text.get_width() + (
                self.background_image_active.get_rect().width / 20)
        self.input_text.y = self.rect.y + (self.rect.height / 6)

        self.input_text.draw(surface)


class Form:
    def __init__(self, background_image, x, y, accept):
        self.background_image = background_image
        self.rect = self.background_image.get_rect()
        self.rect.topleft = (x, y)
        self.username_input = Input('Username: ', pygame.image.load("img/input.png").convert_alpha(),
                                    pygame.image.load("img/input_active.png").convert_alpha(), 0, 0)
        self.address_input = Input('Server address: ', pygame.image.load("img/input.png").convert_alpha(),
                                   pygame.image.load("img/input_active.png").convert_alpha(), 0, 0)
        self.accept_button = Button(0, 0, pygame.image.load("img/join_button.png").convert_alpha(), accept)

    def draw(self, screen):
        screen.blit(self.background_image, (self.rect.x, self.rect.y))

        self.username_input.rect.x = (self.rect.x + (self.rect.width / 2)) - (self.username_input.rect.width / 2)
        self.username_input.rect.y = ((self.rect.y + (self.rect.height / 2)) - (self.username_input.rect.height / 2)
                                      - (self.address_input.rect.width / 6))

        self.address_input.rect.x = (self.rect.x + (self.rect.width / 2)) - (self.address_input.rect.width / 2)
        self.address_input.rect.y = ((self.rect.y + (self.rect.height / 2)) - (self.address_input.rect.height / 2)
                                     + (self.username_input.rect.height / 5))

        self.accept_button.rect.x = (self.rect.x + (self.rect.width / 2)) - (self.accept_button.rect.width / 2)
        self.accept_button.rect.y = ((self.rect.y + (self.rect.height / 2)) - (self.accept_button.rect.height / 2)
                                     + (self.address_input.rect.width / 6))

        self.address_input.draw(screen)
        self.username_input.draw(screen)
        self.accept_button.draw(screen)


class Card:
    def __init__(self, card, x, y):
        self.card = card
        self.__image = pygame.image.load(f"img/{card.value}_{card.type}.png").convert_alpha()
        self.rect = self.__image.get_rect()
        self.rect.topleft = (x, y)

    def update_card(self, card):
        self.card = card
        self.__image = pygame.image.load(f"img/{card.value}_{card.type}.png").convert_alpha()

    def draw(self, screen):
        screen.blit(self.__image, (self.rect.x, self.rect.y))

    def draw_card(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            return True

    def place_card(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            return self.card


class CardDeck:
    def __init__(self, x, y, top_card):
        self.__image = pygame.image.load("img/play_deck.png").convert_alpha()
        self.rect = self.__image.get_rect()
        self.rect.topleft = (x, y)
        self.__draw_deck = Card(connection.components.Card("back", "card"), 0, 0)
        self.top_card = Card(top_card, 0, 0)

    def draw_card(self):
        return self.__draw_deck.place_card()

    def draw(self, screen):
        self.__draw_deck.rect.x = (self.rect.x + (self.rect.width / 2) - (self.__draw_deck.rect.width / 2)
                                   - (self.top_card.rect.width / 2))
        self.__draw_deck.rect.y = self.rect.y + (self.rect.height / 2) - (self.__draw_deck.rect.height / 2)

        self.top_card.rect.x = (self.rect.x + (self.rect.width / 2) - (self.top_card.rect.width / 2)
                                + (self.__draw_deck.rect.width / 2))

        self.top_card.rect.y = self.rect.y + (self.rect.height / 2) - (self.top_card.rect.height / 2)

        screen.blit(self.__image, (self.rect.x, self.rect.y))
        self.__draw_deck.draw(screen)
        self.top_card.draw(screen)


class PlayerDeck:
    def __init__(self, cards, player_nick, x, y):
        self.__cards = []
        self.x = x
        self.y = y

        for card in cards:
            new_card = Card(card, 0, 0)
            self.__cards.append(new_card)

        self.__player_nick = Text(0, 0, player_nick, 'fonts/PixelifySans-Regular.ttf', 31, (0, 0, 0))

    def place_card(self):
        for card in self.__cards:
            placed = card.place_card()
            if placed is not None:
                return placed

    def update_cards(self, cards):
        self.__cards = []

        for card in cards:
            new_card = Card(card, 0, 0)
            self.__cards.append(new_card)

    def draw(self, screen):
        if len(self.__cards) > 0:

            current_x = self.x + (self.__cards[0].rect.width / 5)
            self.y = self.y - self.__cards[0].rect.height - (self.__cards[0].rect.height / 3)

            self.__player_nick.x = current_x
            self.__player_nick.y = self.y - self.__player_nick.text.get_height() - (self.__cards[0].rect.height / 5)

            for card in self.__cards:
                card.rect.x = current_x
                current_x += card.rect.width + (self.__cards[0].rect.width / 5)

                card.rect.y = self.y
                card.draw(screen)

            self.__player_nick.draw(screen)
        else:
            self.__player_nick.x = self.x
            self.__player_nick.y = self.y - self.__player_nick.text.get_height()


class Opponent:
    def __init__(self, opponent):
        self.opponent = opponent
        self.__background_image = pygame.image.load("img/card_back.png").convert_alpha()
        self.rect = self.__background_image.get_rect()
        self.__card_count = Text(0, 0, str(opponent.cards_count), 'fonts/PixelifySans-Regular.ttf', 31, (0, 0, 0))
        self.__label = Text(0, 0, f'Opponent {opponent.player_id}', 'fonts/PixelifySans-Regular.ttf', 31, (0, 0, 0))

    def draw(self, screen):
        self.__card_count.x = self.rect.x + (self.rect.width / 2) - (self.__card_count.text.get_width() / 2)
        self.__card_count.y = (self.rect.y + (self.rect.height / 2) - (self.__card_count.text.get_height() / 2)
                               + (self.__label.text.get_height() * 1.25))

        self.__label.x = self.rect.x
        self.__label.y = self.rect.y + (self.__label.text.get_height() / 4)

        screen.blit(self.__background_image, (self.rect.x, self.rect.y + (self.__label.text.get_height() * 1.25)))
        self.__label.draw(screen)
        self.__card_count.draw(screen)


class Opponents:
    def __init__(self, opponents, x, y):
        self.x = x
        self.y = y
        self.__opponents = []

        for opponent in opponents:
            self.__opponents.append(Opponent(opponent))

    def update_opponents(self, opponents):
        self.__opponents = []

        for opponent in opponents:
            self.__opponents.append(Opponent(opponent))

    def draw(self, screen):
        current_x = self.x
        padding = screen.get_width() / len(self.__opponents)

        for opponent in self.__opponents:
            opponent.rect.x = current_x
            opponent.rect.y = self.y

            opponent.draw(screen)

            current_x += padding


class CurrentPlayer:
    def __init__(self, player, x, y):
        self.__player = player
        self.x = x
        self.y = y
        self.__label = Text(0, 0, '', 'fonts/PixelifySans-Regular.ttf', 31, (0, 0, 0))

    def update_label(self, player, this_player_id):
        self.__player = player
        if self.__player.player_id == this_player_id:
            self.__label.text_string = self.__player.username
        else:
            self.__label.text_string = f'Opponent {self.__player.player_id}'

    def draw(self, screen):
        self.__label.x = self.x - self.__label.text.get_width() - 25
        self.__label.y = self.y - (self.__label.text.get_height() / 2)
        self.__label.draw(screen)


class Type:
    def __init__(self, x, y, image, card_type):
        self.image = pygame.image.load(image).convert_alpha()
        self.type = card_type
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def click(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            return self.type


class ChangeType:
    def __init__(self, image, x, y):
        self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.__buttons = [Type(0, 0, "img/acorn.png", "acorns"),
                          Type(0, 0, "img/bullet.png", "bullets"),
                          Type(0, 0, "img/heart.png", "hearts"),
                          Type(0, 0, "img/leaf.png", "leafs")]
        self.is_visible = False

    def check_buttons(self):
        for button in self.__buttons:
            result = button.click()
            if result is not None:
                return result

    def draw(self, screen):
        if not self.is_visible:
            return

        screen.blit(self.image, (self.rect.x, self.rect.y))

        current_x = self.rect.x + ((self.rect.width - 100) / len(self.__buttons))

        for button in self.__buttons:
            button.rect.x = current_x
            button.rect.y = self.rect.y + 10
            button.draw(screen)

            current_x += ((self.rect.width - 20) / len(self.__buttons))


class CurrentType:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.__buttons = {"acorns": Type(0, 0, "img/acorn.png", "acorns"),
                          "bullets": Type(0, 0, "img/bullet.png", "bullets"),
                          "hearts": Type(0, 0, "img/heart.png", "hearts"),
                          "leafs": Type(0, 0, "img/leaf.png", "leafs")}

    def draw(self, screen, type):
        to_draw = self.__buttons[type]

        to_draw.rect.x = self.x - (to_draw.rect.width / 2)
        to_draw.rect.y = self.y

        to_draw.draw(screen)
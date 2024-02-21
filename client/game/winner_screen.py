import pygame
import game.components as components


class WinnerScreen:
    def __init__(self, surface, join, go_back):
        self.__surface = surface
        self.__go_back_button = components.Button(0, 0, pygame.image.load("img/back_button.png").convert_alpha(),
                                                  go_back)
        self.__join_again_button = components.Button(0, 0, pygame.image.load("img/join_again_button.png")
                                                     .convert_alpha(), join)

        self.__winner_text = components.Text(0, 0, '', 'fonts/PixelifySans-Regular.ttf', 72, (0, 0, 0))
        self.winner = None

    def update_winner_text(self, winner):
        self.__winner_text.text_string = f'Winner is {winner}'

    def check_button(self):
        self.__go_back_button.click()
        self.__join_again_button.click()

    def draw(self):
        self.__surface.fill((255, 249, 224))

        self.__go_back_button.rect.x = (self.__surface.get_width() / 2) - (self.__go_back_button.rect.width / 2)
        self.__go_back_button.rect.y = ((self.__surface.get_height()) - (self.__go_back_button.rect.height * 1.5)
                                        - (self.__join_again_button.rect.height * 1.5))

        self.__join_again_button.rect.x = (self.__surface.get_width() / 2) - (self.__join_again_button.rect.width / 2)
        self.__join_again_button.rect.y = (self.__surface.get_height()) - (self.__join_again_button.rect.height * 1.5)

        self.__winner_text.x = (self.__surface.get_width() / 2) - (self.__winner_text.text.get_width() / 2)
        self.__winner_text.y = (self.__surface.get_height() / 2) - (self.__winner_text.text.get_height() / 2)

        self.__go_back_button.draw(self.__surface)
        self.__join_again_button.draw(self.__surface)
        self.__winner_text.draw(self.__surface)


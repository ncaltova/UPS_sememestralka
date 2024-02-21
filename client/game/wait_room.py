import pygame
import game.components as components


class WaitRoom:
    def __init__(self, surface, go_back):
        self.__surface = surface
        self.__heading = components.Text(0, 0, 'Waiting for other players',
                                         'fonts/PixelifySans-Regular.ttf', 41, (0, 0, 0))
        self.__go_back_button = components.Button(0, 0, pygame.image.load("img/back_button.png").convert_alpha(),
                                                  go_back)
        self.__dots = components.Text(0, 0, '...', 'fonts/PixelifySans-Regular.ttf', 72, (0, 0, 0))

    def check_button(self):
        self.__go_back_button.click()

    def draw(self):
        self.__surface.fill((255, 249, 224))

        self.__heading.x = (self.__surface.get_width() / 2) - (self.__heading.text.get_width() / 2)
        self.__heading.y = self.__heading.text.get_height() / 4

        self.__dots.x = (self.__surface.get_width() / 2) - (self.__dots.text.get_width() / 2)
        self.__dots.y = (self.__surface.get_height() / 2) - (self.__dots.text.get_height() / 2)

        self.__go_back_button.rect.x = (self.__surface.get_width() / 2) - (self.__go_back_button.rect.width / 2)
        self.__go_back_button.rect.y = (self.__surface.get_height()) - (self.__go_back_button.rect.height * 1.5)

        self.__heading.draw(self.__surface)
        self.__dots.draw(self.__surface)
        self.__go_back_button.draw(self.__surface)

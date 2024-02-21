import pygame
import game.components as components


class Menu:
    def __init__(self, surface, leave_action, join_action):
        self.__surface = surface
        self.__leave_button = components.Button(0, 0, pygame.image.load("img/leave_game_button.png").convert_alpha(),
                                                leave_action)
        self.__join_button = components.Button(0, 0, pygame.image.load("img/join_game_button.png").convert_alpha(),
                                               join_action)
        self.__heading = components.Text(0, 0, 'Mau-Mau',
                                         'fonts/PixelifySans-Regular.ttf', 72, (0, 0, 0))

        self.validation = components.Text(0, 0, '', 'fonts/PixelifySans-Regular.ttf', 30, (186, 65, 0))

    def draw(self):
        # Setting background
        self.__surface.fill((255, 249, 224))

        self.__heading.x = (self.__surface.get_width() / 2) - (self.__heading.text.get_width() / 2)
        self.__heading.y = self.__heading.text.get_height() / 4

        self.validation.x = (self.__surface.get_width() / 2) - (self.validation.text.get_width() / 2)
        self.validation.y = self.__heading.y + (self.validation.text.get_height() * 2)

        self.__join_button.rect.x = (self.__surface.get_width() / 2) - (self.__join_button.rect.width / 2)
        self.__join_button.rect.y = ((self.__surface.get_height() / 2) - (self.__join_button.rect.height / 2)
                                     - (self.__leave_button.rect.height / 1.5) + (self.__heading.text.get_height() / 3))

        self.__leave_button.rect.x = (self.__surface.get_width() / 2) - (self.__leave_button.rect.width / 2)
        self.__leave_button.rect.y = ((self.__surface.get_height() / 2) - (self.__leave_button.rect.height / 2)
                                      + (self.__join_button.rect.height / 1.5) + (self.__heading.text.get_height() / 3))

        self.__join_button.draw(self.__surface)
        self.__leave_button.draw(self.__surface)
        self.__heading.draw(self.__surface)
        self.validation.draw(self.__surface)

    def check_events(self):
        self.__join_button.click()
        self.__leave_button.click()

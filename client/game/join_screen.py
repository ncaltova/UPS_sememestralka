import pygame
import game.components as components


class JoinScreen:
    def __init__(self, surface, go_back, connect):
        self.__surface = surface
        self.form = components.Form(pygame.image.load("img/form_background.png").convert_alpha(), 0, 0, connect)
        self.__heading = components.Text(0, 0, 'Join new game',
                                         'fonts/PixelifySans-Regular.ttf', 72, (0, 0, 0))
        self.validation = components.Text(0, 0, '', 'fonts/PixelifySans-Regular.ttf', 30, (186, 65, 0))
        self.__go_back_button = components.Button(0, 0, pygame.image.load("img/back_button.png").convert_alpha(),
                                                  go_back)

    def draw(self):
        self.__surface.fill((255, 249, 224))

        self.__heading.x = (self.__surface.get_width() / 2) - (self.__heading.text.get_width() / 2)
        self.__heading.y = self.__heading.text.get_height() / 4

        self.validation.x = (self.__surface.get_width() / 2) - (self.validation.text.get_width() / 2)
        self.validation.y = self.__heading.y + (self.validation.text.get_height() * 2.25)

        self.form.rect.x = (self.__surface.get_width() / 2) - (self.form.rect.width / 2)
        self.form.rect.y = (self.__surface.get_height() / 2) - (self.form.rect.height / 2)

        self.__go_back_button.rect.x = (self.__surface.get_width() / 2) - (self.__go_back_button.rect.width / 2)
        self.__go_back_button.rect.y = (self.__surface.get_height()) - (self.__go_back_button.rect.height * 1.5)

        self.form.draw(self.__surface)
        self.__heading.draw(self.__surface)
        self.validation.draw(self.__surface)
        self.__go_back_button.draw(self.__surface)

    def check_buttons(self):
        self.form.accept_button.click()
        self.__go_back_button.click()

    def check_inputs(self):
        self.form.address_input.set_active()
        self.form.username_input.set_active()

    def input_text(self, event):
        if self.form.address_input.is_active:
            self.form.address_input.input(event)
        elif self.form.username_input.is_active:
            self.form.username_input.input(event)

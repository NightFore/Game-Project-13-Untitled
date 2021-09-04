import pygame
from os import path

from Class import *
from Function import *

def init_menu(game, menu, clear=True, ui=True, button=True):
    if clear:
        clear_menu(game)
    if ui:
        if menu in game.ui_dict:
            for ui in game.ui_dict[menu]:
                UI(game, game.ui_dict, game.uis, data=menu, item=ui)
    if button:
        if menu in game.button_dict:
            for button in game.button_dict[menu]:
                Button(game, game.button_dict, game.buttons, data=menu, item=button)

def clear_menu(game):
    for sprite in game.all_sprites:
        sprite.kill()

def main_menu(game, menu):
    init_menu(game, menu)

def pause_menu(game, menu):
    game.paused = not game.paused



MENU_DICT = {
    "main_menu": main_menu,
    "pause_menu": pause_menu,
}

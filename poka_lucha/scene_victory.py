from . import scene_base
from . import music
from .resload import get_resource
from .ent_button import Button
from .entity import Entity
import math
import pygame

class SceneVictory(scene_base.Scene):

    def __init__(self, winner:int, manager = None):
        super().__init__("victory", manager)

        self.winner = winner

        self.bg_color = pygame.Color("#040303")

        self.bg_group = pygame.sprite.Group()
        self.hud_group = pygame.sprite.Group()

        self.create_background()
        self.create_buttons()

    def create_background(self):
        self.bg = Entity((0, 0), get_resource("title/bg.png"), group=self.bg_group)
        self.entities.append(self.bg)

    def create_buttons(self):
        #self.btn_quit = Button("Quit", (960, 640), self.on_quit, group=self.hud_group)
        #self.entities.append(self.btn_quit)
        pass

    def handle_event(self, event):
        super().handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.on_quit()

    def update(self, dt):
        return super().update(dt)

    def on_quit(self):
        from .scene_title import SceneTitle
        self.manager.next_scene = SceneTitle(self.manager)

    def render(self, surface):
        return super().render(surface)
from . import scene_base
from . import music
from .resload import get_resource
from .ent_button import Button
import math

import pygame
from typing import Any

BGM_VOL = 0.2

class SceneCredits(scene_base.Scene):
    """
    Gameplay scene:
    """
    def __init__(self, manager: Any = None):
        super().__init__("gameplay", manager)
        self.bg_color = pygame.Color("darkslateblue")
        self.time = 0


    def enter(self, *args, **kwargs):
        self.bg_image = get_resource("title/pocalucha.png")

        self.entities.append(
            Button(
            1920/8-get_resource("title/button_bg.png").get_width()/8, 850,
            get_resource("title/restart.png"),
            "",
            callback=lambda: self.on_title(),
            font=pygame.font.SysFont("Arial", 50)
            )
        )

    def on_title(self):
        music.fadeout(200)
        from poka_lucha.scene_title import SceneTitle
        self.manager.next_scene = SceneTitle(self.manager)

    def exit(self):
        pass

    def pause(self):
        super().pause()

    def resume(self):
        super().resume()

    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                # stop/fade title music
                music.fadeout(200)

               
    def update(self, dt: float):
        super().update(dt)
        self.time += dt
        if self.paused:
            return
        pass

    def render(self, surface: pygame.Surface):
        surface.fill(self.bg_color)
        surface.blit(self.bg_image, (0, 0))
        sw, sh = surface.get_size()
        super().render(surface)
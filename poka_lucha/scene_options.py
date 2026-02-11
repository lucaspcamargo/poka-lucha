from . import scene_base
from . import music
from .resload import get_resource
from .ent_button import Button
import math

import pygame
from typing import Any

BGM_VOL = 0.2

class SceneOptions(scene_base.Scene):
    """
    Gameplay scene:
    """
    def __init__(self, manager: Any = None):
        super().__init__("gameplay", manager)
        self.bg_color = pygame.Color("darkslateblue")
        self.time = 0

    ##img_sound = pygame.image.load("title/sound.png").convert_alpha()
    ##img_nosound = pygame.image.load("title/nosound.png").convert_alpha()


    def enter(self, *args, **kwargs):
        self.bg_image = get_resource("title/bg.png")
        self.main_image = get_resource("title/main.png")

        self.entities.append(
            Button(
            1920/8-get_resource("title/button_bg.png").get_width()/8, 850,
            get_resource("title/restart.png"),
            "",
            callback=lambda: self.on_title(),
            font=pygame.font.SysFont("Arial", 50)
            )
        )

        self.botaoMute = Button(
            1920/2-get_resource("title/button_bg.png").get_width()/2+175, 600,
            get_resource("title/sound.png"),
            "",
            callback=lambda: self.on_mute(), 
            font=pygame.font.SysFont("Arial", 50)
        )


        self.entities.append(
            self.botaoMute
        )

    def on_title(self):
        from poka_lucha.scene_title import SceneTitle
        self.manager.next_scene = SceneTitle(self.manager)

    def on_mute(self):
        ##self.botaoMute.image.load("nosound.png") 
        pass
        

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
        iw, ih = self.main_image.get_size()
        surface.blit(self.main_image, ((sw - iw) // 2, (sh - ih) // 2 - 180 + math.sin(self.time) * 20))
        super().render(surface)
from poka_lucha.scene_gameplay import SceneGameplay
from poka_lucha.scene_options import SceneOptions
from poka_lucha.scene_credits import SceneCredits
from . import scene_base
from . import music
from .resload import get_resource
from .ent_button import Button
import math

import pygame
from typing import Any

BGM_VOL = 0.2

class SceneTitle(scene_base.Scene):
    """
    Gameplay scene:
    """
    def __init__(self, manager: Any = None):
        super().__init__("gameplay", manager)
        self.bg_color = pygame.Color("darkslateblue")
        self.time = 0


    def enter(self, *args, **kwargs):
        self.bg_image = get_resource("title/bg.png")
        self.main_image = get_resource("title/main.png")
        music.play("bgm/menu_prev.mp3")
        music.set_bgm_volume(BGM_VOL)
        self.entities.append(
            Button(
            1920/2-get_resource("title/play.png").get_width()/2, 500,
            get_resource("title/play.png"),
            "",
            callback=lambda: self.on_play()
            )
        )

        self.entities.append(
            Button(
            1920/2-get_resource("title/button_bg.png").get_width()/2, 850,
            get_resource("title/button_bg.png"),
            "opções",
            callback=lambda: self.on_options(),
            font=pygame.font.SysFont("Arial", 50)
            )
        )

        self.entities.append(
            Button(
            1920/2-get_resource("title/button_bg.png").get_width()/2, 675,
            get_resource("title/button_bg.png"),
            "Créditos",
            callback=lambda: self.on_credits(), 
            font=pygame.font.SysFont("Arial", 50)
            )
        )

    def on_play(self):
        music.stop()
        self.manager.next_scene = SceneGameplay(self.manager)

    def on_options(self):
        self.manager.next_scene = SceneOptions(self.manager)

    def on_credits(self):
        self.manager.next_scene = SceneCredits(self.manager)

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

                self.manager.next_scene = SceneGameplay(self.manager)

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
from . import scene_base
from .ent_particles import ParticleSystem
from . import music
from .resload import load_resources_init, load_resource
from .ent_button import Button
import math

import pygame
from typing import Any, Callable

RES_DIR = "./res/"

class SceneResload(scene_base.Scene):
    """
    Gameplay scene:
    """
    def __init__(self, next_scene: scene_base.Scene, manager: Any = None, file_filter: None or Callable = None):
        super().__init__("gameplay", manager)
        self.bg_color = pygame.Color("black")
        self.load_color = pygame.Color("yellow")
        self.load_bg_color = pygame.Color("#222222")
        self.files = load_resources_init(RES_DIR)
        if file_filter is not None:
            self.files = list(filter(file_filter, self.files))
        self.total = len(self.files)
        self.done = 0
        self.last_frame = pygame.time.get_ticks()
        self.next_scene = next_scene

        self.ent_particles = ParticleSystem()
        #self.entities.append(self.ent_particles)

    def enter(self, *args, **kwargs):
        pass

    def exit(self):
        pass

    def pause(self):
        super().pause()

    def resume(self):
        super().resume()

    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)

    def update(self, dt: float):
        super().update(dt)
        for p in self.files[self.done:]:
            load_resource(p, RES_DIR)
            self.done += 1
            print(f"Loaded {self.done}/{self.total}: {p}")
            if pygame.time.get_ticks() - self.last_frame > 50:
                self.last_frame = pygame.time.get_ticks()
                break # let's update gfx at about 20 fps
        # loop ended, we must have finished it all
        if self.done == self.total:
            self.manager.next_scene = self.next_scene

    def render(self, surface: pygame.Surface):
        surface.fill(self.bg_color)
        pygame.draw.rect(surface, self.load_bg_color, pygame.Rect(50, self.height // 2 - 15, self.width - 100, 30))
        pygame.draw.rect(surface, self.load_color, pygame.Rect(50, self.height // 2 - 15, int((self.done / self.total) * (self.width - 100)), 30))
        show_idx = min(self.done, self.total - 1)
        txt_surf = self.manager.dbg_font.render(f"Loaded: {self.files[show_idx]}", False, self.load_color, None)
        rect = txt_surf.get_rect()
        surface.blit(txt_surf, (50, self.height // 2 - 50))

        super().render(surface)



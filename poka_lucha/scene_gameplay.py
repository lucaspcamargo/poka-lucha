import math
from poka_lucha.ent_bar import Bar
from . import scene_base
from . import music
from .resload import get_resource
from .entity import Entity
from .ent_guy import LittleGuy

import pygame
import sys
from typing import Any

BGM_VOL = 0.2

MAX_HEALTH = 100
MAX_STAMINA = 20
DBG_GAMEPLAY = '--debug' in sys.argv or '--debug-gameplay' in sys.argv

class SceneGameplay(scene_base.Scene):
    """
    Gameplay scene:
    """
    def __init__(self, manager: Any = None):
        super().__init__("gameplay", manager)

        self.bg_color = pygame.Color("#222222")

        self.bg_group = pygame.sprite.Group()
        self.hud_group = pygame.sprite.Group()

        self.inv_flip = False
        self.p1_health = MAX_HEALTH
        self.p2_health = MAX_HEALTH
        self.p1_stamina = MAX_STAMINA
        self.p2_stamina = MAX_STAMINA
        self.p1_lives = 3
        self.p2_lives = 3

    def enter(self, *args, **kwargs):
        music.play("bgm/loop.ogg")
        music.set_bgm_volume(BGM_VOL)

        self.lower_bg = Entity((-255, 0), get_resource("bgs/new3.png"), group=self.bg_group)
        self.lower_bg.parallax = 0.5
        self.entities.append(self.lower_bg)

        #self.middle_bg = Entity((-255, 0), get_resource("bgs/new1.png"), group=self.bg_group)
        #self.middle_bg.parallax = 0.63
        #self.entities.append(self.middle_bg)

        self.crowd_imgs = [get_resource(f"bgs/crowd/{i}.png") for i in range(3)]
        self.crowd_timer = 0.0

        self.middle_bg = Entity((-275, 150), self.crowd_imgs[0], group=self.bg_group)
        self.middle_bg.parallax = 0.63
        self.entities.append(self.middle_bg)


        self.main_bg = Entity((-275, 1080-500), get_resource("bgs/ring.png"), group=self.bg_group)
        self.main_bg.parallax = 0.8
        self.entities.append(self.main_bg)

        self.ent_p1 = LittleGuy(0, False, (400, 1000-LittleGuy.DIM_Y,))
        self.ent_p2 = LittleGuy(1, True, (1920-400-LittleGuy.DIM_X, 1000-LittleGuy.DIM_Y,))
        self.entities.append(self.ent_p1)
        self.entities.append(self.ent_p2)

        self.hud_bg = Entity((0, 0), get_resource("bgs/hud.png"), group=self.hud_group)
        self.hud_bg.scroll = False
        self.ent_p1l = Bar((80, 68), (728, 32), max_value=MAX_HEALTH, current_value=MAX_HEALTH, group=self.hud_group)
        self.ent_p1s = Bar((75, 120), (479, 20), max_value=MAX_STAMINA, current_value=MAX_STAMINA, color=pygame.Color("yellow"), group=self.hud_group)
        self.ent_p2l = Bar((1094, 68), (728, 32), max_value=MAX_HEALTH, current_value=MAX_HEALTH, ltr = True, group=self.hud_group)
        self.ent_p2s = Bar((1348, 120), (479, 20), max_value=MAX_STAMINA, current_value=MAX_STAMINA, ltr = True, color=pygame.Color("yellow"), group=self.hud_group)
        self.entities.append(self.hud_bg)
        self.entities.append(self.ent_p1l)
        self.entities.append(self.ent_p1s)
        self.entities.append(self.ent_p2l)
        self.entities.append(self.ent_p2s)

        self.heart_icon = get_resource("bgs/hud_heart.png")
        

    def exit(self):
        music.fadeout(1000)

    def pause(self):
        super().pause()

    def resume(self):
        super().resume()

    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)

    def update(self, dt: float):
        
        if self.paused:
            return
        
        super().update(dt)

        self.crowd_timer += dt
        crowd_seq = [0, 1, 2, 1]
        self.middle_bg.image = self.crowd_imgs[crowd_seq[int((self.crowd_timer*3 ) % 4)]]

        if self.ent_p1.hitbox is not None:
            if self.ent_p1.hitbox.colliderect(self.ent_p2.rect):
                self.ent_p2.receive_hit(self.ent_p1.hit_damage, 50)
        if self.ent_p2.hitbox is not None:
            if self.ent_p2.hitbox.colliderect(self.ent_p1.rect):
                self.ent_p1.receive_hit(self.ent_p2.hit_damage, 50)

        # update internal stats
        self.p1_health = self.ent_p1.health
        self.p1_stamina = self.ent_p1.stamina
        self.p2_health = self.ent_p2.health
        self.p2_stamina = self.ent_p2.stamina

        # update bars
        self.ent_p1l.current_value = self.p1_health
        self.ent_p1s.current_value = self.p1_stamina
        self.ent_p2l.current_value = self.p2_health
        self.ent_p2s.current_value = self.p2_stamina

        prev_inv_flip = self.inv_flip
        inv_flip = self.ent_p1.pos.x > self.ent_p2.pos.x
        if inv_flip != prev_inv_flip:
            self.inv_flip = inv_flip
            self.ent_p1.set_inv_flip(self.inv_flip)
            self.ent_p2.set_inv_flip(self.inv_flip)

        # check if turn must end
        if self.ent_p1.state == self.ent_p1.STATE_DEAD or self.ent_p2.state == self.ent_p2.STATE_DEAD:
            p1_died = self.ent_p1.state == self.ent_p1.STATE_DEAD
            dead_time = self.ent_p1.state_timer if p1_died else self.ent_p2.state_timer
            if dead_time > 4.0:
                self.reset_round(p1_died)

        if DBG_GAMEPLAY:
            # move camera with arrow keys
            keys = pygame.key.get_pressed()
            if hasattr(self, "cam_pos"):
                speed = 100.0  # pixels per second
                dx = 0.0
                if keys[pygame.K_LEFT]:
                    dx -= speed * dt
                if keys[pygame.K_RIGHT]:
                    dx += speed * dt
                self.cam_pos.x += dx

        # middle point
        middle = (self.ent_p1.rect.centerx + self.ent_p2.rect.centerx - 1920) / 2
        self.cam_pos.x = (middle-self.cam_pos.x) * math.pow(0.1, dt)

        # cam limits
        if self.cam_pos.x < -339:
            self.cam_pos.x = -339
        if self.cam_pos.x > 339:
            self.cam_pos.x = 339

    def reset_round(self, p1_died: bool):
        if p1_died:
            self.p1_lives -= 1
        else:
            self.p2_lives -= 1

        if self.p1_lives <= 0 or self.p2_lives <= 0:
            self.end_game(p1_died)

        self.ent_p1.reset()
        self.ent_p2.reset()

    def end_game(self, p1_died: bool):
        from .scene_title import SceneTitle
        self.manager.next_scene = SceneTitle(self.manager)

    def render(self, surface: pygame.Surface):
        surface.fill(self.bg_color)
        super().render(surface)

        for i in range(self.p1_lives):
            surface.blit(self.heart_icon, (70 + i * (self.heart_icon.get_width() + 15), 157))

        for i in range(self.p2_lives):
            surface.blit(self.heart_icon, (1802 - i * (self.heart_icon.get_width() + 15), 157))

        if DBG_GAMEPLAY:
            self.render_debug_info(surface)

    def render_debug_info(self, surface: pygame.Surface):
        font = self.manager.dbg_font
        lines = []

        # basic scene info
        lines.append(f"inv_flip: {self.inv_flip}")

        lines.append(f"camera pos: {self.cam_pos.x},{self.cam_pos.y}")

        # player positions if available
        for pname in ("ent_p1", "ent_p2"):
            ent = getattr(self, pname, None)
            if ent is None:
                lines.append(f"{pname}: <none>")
            else:
                pos = getattr(ent, "pos", None)
                if pos is not None and hasattr(pos, "x"):
                    lines.append(f"{pname} pos: {pos.x:.1f},{pos.y:.1f}")
                else:
                    lines.append(f"{pname}: {type(ent).__name__}")

        # draw semi-transparent background and render debug lines
        padding = 6
        line_h = 18
        w = 320
        h = line_h * len(lines) + padding * 2
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surface.blit(bg, (10, 10))

        for i, line in enumerate(lines):
            txt = font.render(line, True, pygame.Color("white"))
            surface.blit(txt, (10 + padding, 10 + padding + i * line_h))
from . import scene_base
from . import music
from .resload import get_resource

import pygame
from typing import Any

NUM_CHARS = 2  # char 2 not yet implemented
SW, SH = 1920, 1080

# P1: A/D to cycle, Q/W/E to confirm  (mirrors gameplay bindings)
# P2: J/L to cycle, U/I/O to confirm
P1_LEFT   = pygame.K_a
P1_RIGHT  = pygame.K_d
P1_OK     = {pygame.K_q, pygame.K_w, pygame.K_e}

P2_LEFT   = pygame.K_j
P2_RIGHT  = pygame.K_l
P2_OK     = {pygame.K_u, pygame.K_i, pygame.K_o}

PORTRAIT_SCALE = 0.45
PANEL_W = SW // 2

COL_READY  = pygame.Color("#44ff88")
COL_UNREADY = pygame.Color("#aaaaaa")
COL_DARK   = pygame.Color("#111122")
COL_LABEL  = pygame.Color("#ffffff")
COL_ARROW  = pygame.Color("#ffdd55")


class SceneCharSelect(scene_base.Scene):
    def __init__(self, manager: Any = None):
        super().__init__("charselect", manager)
        self.time = 0.0
        self.p1_sel = 0
        self.p2_sel = 1
        self.p1_ready = False
        self.p2_ready = False

    def enter(self, *args, **kwargs):
        self.bg_color = pygame.Color("darkslateblue")
        self.portraits = [
            get_resource(f"chr/{i}/cover.png") for i in range(NUM_CHARS)
        ]
        self.font_big   = pygame.font.SysFont("Arial", 47, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 26)
        self.font_hint  = pygame.font.SysFont("Arial", 20)

    def exit(self):
        pass

    def pause(self):
        super().pause()

    def resume(self):
        super().resume()

    def handle_event(self, event: pygame.event.Event):
        if event.type != pygame.KEYDOWN:
            return

        key = event.key

        # P1 controls
        if not self.p1_ready:
            if key == P1_LEFT:
                self.p1_sel = (self.p1_sel - 1) % NUM_CHARS
            elif key == P1_RIGHT:
                self.p1_sel = (self.p1_sel + 1) % NUM_CHARS
            elif key in P1_OK:
                self.p1_ready = True
        else:
            if key in P1_OK:
                self.p1_ready = False  # de-select

        # P2 controls
        if not self.p2_ready:
            if key == P2_LEFT:
                self.p2_sel = (self.p2_sel - 1) % NUM_CHARS
            elif key == P2_RIGHT:
                self.p2_sel = (self.p2_sel + 1) % NUM_CHARS
            elif key in P2_OK:
                self.p2_ready = True
        else:
            if key in P2_OK:
                self.p2_ready = False  # de-select

        if self.p1_ready and self.p2_ready:
            self._start_game()

    def _start_game(self):
        music.fadeout(300)
        from poka_lucha.scene_gameplay import SceneGameplay
        self.manager.next_scene = SceneGameplay(
            self.manager,
            p1_char=self.p1_sel,
            p2_char=self.p2_sel,
        )

    def update(self, dt: float):
        super().update(dt)
        self.time += dt

    def _draw_panel(self, surface: pygame.Surface, player: int):
        sel     = self.p1_sel   if player == 1 else self.p2_sel
        ready   = self.p1_ready if player == 1 else self.p2_ready
        panel_x = 0 if player == 1 else PANEL_W

        # background panel
        panel_rect = pygame.Rect(panel_x, 0, PANEL_W, SH)
        panel_surf = pygame.Surface((PANEL_W, SH), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 30, 180))
        surface.blit(panel_surf, panel_rect)

        cx = panel_x + PANEL_W // 2

        # player label
        label = f"PLAYER {player}"
        lbl_surf = self.font_big.render(label, True, COL_READY if ready else COL_LABEL)
        surface.blit(lbl_surf, lbl_surf.get_rect(centerx=cx, top=60))

        # portrait
        portrait = self.portraits[sel]
        pw = int(portrait.get_width()  * PORTRAIT_SCALE)
        ph = int(portrait.get_height() * PORTRAIT_SCALE)
        scaled = pygame.transform.scale(portrait, (pw, ph))
        portrait_rect = scaled.get_rect(centerx=cx, centery=SH // 2 - 30)
        surface.blit(scaled, portrait_rect)

        # navigation arrows
        left_arrow  = "<"
        right_arrow = ">"
        a_surf_l = self.font_big.render(left_arrow,  True, COL_ARROW)
        a_surf_r = self.font_big.render(right_arrow, True, COL_ARROW)
        surface.blit(a_surf_l, a_surf_l.get_rect(centery=SH // 2 - 30, right=portrait_rect.left - 20))
        surface.blit(a_surf_r, a_surf_r.get_rect(centery=SH // 2 - 30, left=portrait_rect.right + 20))

        # char index dots
        dot_y = portrait_rect.bottom + 40
        dot_r = 14
        dot_gap = 48
        total_w = NUM_CHARS * dot_gap - (dot_gap - dot_r * 2)
        start_x = cx - total_w // 2 + dot_r
        for i in range(NUM_CHARS):
            color = COL_ARROW if i == sel else COL_UNREADY
            pygame.draw.circle(surface, color, (start_x + i * dot_gap, dot_y), dot_r)

        # ready / hint text
        if ready:
            status_surf = self.font_big.render("PRONTO!", True, COL_READY)
        else:
            hint_keys = "A/D  +  Q/W/E" if player == 1 else "J/L  +  U/I/O"
            status_surf = self.font_hint.render(hint_keys, True, COL_UNREADY)
        surface.blit(status_surf, status_surf.get_rect(centerx=cx, top=dot_y + 20))

    def render(self, surface: pygame.Surface):
        surface.fill(self.bg_color)

        self._draw_panel(surface, 1)
        self._draw_panel(surface, 2)

        # centre divider
        pygame.draw.line(surface, COL_UNREADY, (PANEL_W, 80), (PANEL_W, SH - 80), 3)

        # top title
        title_surf = self.font_big.render("ESCOLHA SEU LUTADOR", True, COL_LABEL)
        tr = title_surf.get_rect(centerx=SW // 2, top=10)
        pygame.draw.rect(surface, COL_DARK, tr.inflate(40, 14), border_radius=8)
        surface.blit(title_surf, tr)

        super().render(surface)

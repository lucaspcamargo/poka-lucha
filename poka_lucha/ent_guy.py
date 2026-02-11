import math
from .entity import Entity
from .ent_animspr import AnimatedSprite
from .resload import get_resource

import pygame
import sys

# REMEMBER, ROBOT! CHARACTERS DONT JUMP IN THIS GAME!!!

DBG_COLL = '--debug' in sys.argv or '--debug-coll' in sys.argv

CHAR_CONFIG = {
    0: {
        'walk_speed': 200.0,
        'punch_dmg': 7,
        'punch_start_x': 0.5,
        'punch_end_x': 1.3,
        'punch_stamina': 4,
        'punch_start_frame': 10,
        'punch_end_frame': 15,
        'kick_dmg': 10,
        'kick_stamina': 6,
        'kick_start_x': 0.5,
        'kick_end_x': 1.5,
        'kick_start_frame': 8,
        'kick_end_frame': 18,
        'block_stamina': 2,
        'block_start_frame': 3,
        'block_hold_frame': 6,
        'block_end_frame': 9,
        "block_damage_divider": 3,
        "knockback_multiplier": 1.0
    },
    1: {
        'walk_speed': 200.0,
        'punch_dmg': 7,
        'punch_start_x': 0.5,
        'punch_end_x': 1.3,
        'punch_stamina': 4,
        'punch_start_frame': 10,
        'punch_end_frame': 15,
        'kick_dmg': 10,
        'kick_stamina': 6,
        'kick_start_x': 0.5,
        'kick_end_x': 1.5,
        'kick_start_frame': 8,
        'kick_end_frame': 18,
        'block_stamina': 2,
        'block_start_frame': 3,
        'block_hold_frame': 6,
        'block_end_frame': 9,
        "block_damage_divider": 3,
        "knockback_multiplier": 1.0
    }
}


class LittleGuy(AnimatedSprite):

    DIM_X = 300
    DIM_Y = 600
    MIN_X = -260
    MAX_X = 1920 - MIN_X - DIM_X

    """
    Simple fighting-game actor with a small state machine.
    Construct with an integer character id: LittleGuy(char_id, pos=(x,y))
    """
    # possible states (jump removed)
    STATE_IDLE = "idle"
    STATE_WALK = "walk"
    STATE_PUNCH = "punch"
    STATE_KICK = "kick"
    STATE_BLOCK = "block"
    STATE_HIT = "hit"
    STATE_DEAD = "dead"

    INPUT_MAP = [
        {"left": pygame.K_a, "right": pygame.K_d, "punch": pygame.K_r, "kick": pygame.K_t, "block": pygame.K_y},  # Player 1
        {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "punch": pygame.K_KP1, "kick": pygame.K_KP2, "block": pygame.K_KP3},  # Player 2
    ]


    def __init__(self, char_id: int, p2: bool=False, pos=(0, 0)):
        self.animations = LittleGuy._make_anims(char_id)
        super().__init__(pos, self.animations, initial=self.STATE_IDLE)
        # identity
        self.char_id = int(char_id)
        self.p2 = p2  # whether we are player 2 (for controls)
        self.input_map = self.INPUT_MAP[1] if p2 else self.INPUT_MAP[0]
        self.input_states = {key: False for key in self.input_map.keys()}

        # restoration state
        self.start_pos = pos
        self.orig_frame_time = self.frame_time

        # state machine init
        self.state = self.STATE_IDLE
        self.facing = -1 if self.p2 else 1  # 1 = right, -1 = left
        self.state_timer = 0.0

        self.reset()

        # configuration
        self.walk_speed = 140.0
        self.attack_duration = 0.35
        self.hit_recovery = 0.5

        # hitbox and damage props
        self.hitbox: pygame.Rect = None
        self.hit_damage: int = 0
        self.blocking = False
        self.already_block_dmg = False

    def set_inv_flip(self, inv_flip: bool):
        self.facing = -1 if (self.p2 ^ inv_flip) else 1  # 1 = right, -1 = left

    def calc_offset_center(self):
        """Calculate offset to center the sprite in the rect."""
        anim_frame = self.animations[self.STATE_IDLE]["frames"][0]
        frame_w, frame_h = anim_frame.get_size()
        offset_x = (self.size.width - frame_w) // 2
        offset_y = (self.size.height - frame_h) // 2
        return pygame.math.Vector2(offset_x, offset_y)

    @classmethod
    def _make_anims(cls, char_id: int):
        if char_id == 0:
            animations = {
                cls.STATE_IDLE: AnimatedSprite.anim_from_path_template(f"chr/{char_id}/idle/{{:04d}}.png", 23),
                cls.STATE_WALK: AnimatedSprite.anim_from_path_template(f"chr/{char_id}/walk/{{:04d}}.png", 23),
                cls.STATE_PUNCH: AnimatedSprite.anim_from_path_template(f"chr/{char_id}/punch/{{:04d}}.png", 30),
                cls.STATE_KICK: AnimatedSprite.anim_from_path_template(f"chr/{char_id}/kick/{{:04d}}.png", 25),
                cls.STATE_BLOCK: AnimatedSprite.anim_from_path_template(f"chr/{char_id}/block/{{:04d}}.png", 13, 0),
                cls.STATE_HIT: AnimatedSprite.anim_from_path_template(f"chr/{char_id}/hit/{{:04d}}.png", 18, 0),
                cls.STATE_DEAD: AnimatedSprite.anim_from_path_template(f"chr/{char_id}/death/{{:04d}}.png", 36, 0),
            }
        elif char_id == 1:
            animations = {
                cls.STATE_IDLE: AnimatedSprite.anim_from_path_template(f"chr/{char_id}/idle/{{:04d}}.png", 13, 0),
                cls.STATE_WALK: AnimatedSprite.anim_from_path_template(f"chr/{char_id}/walk/{{:04d}}.png", 18, 0),
                cls.STATE_PUNCH: AnimatedSprite.anim_from_path_template(f"chr/{char_id}/punch/{{:04d}}.png", 33, 0),
                cls.STATE_KICK: AnimatedSprite.anim_from_path_template(f"chr/{char_id}/kick/{{:04d}}.png", 24, 0),
                cls.STATE_BLOCK: AnimatedSprite.anim_from_path_template(f"chr/{char_id}/hit/{{:04d}}.png", 13, 0), # FIXME
                cls.STATE_HIT: AnimatedSprite.anim_from_path_template(f"chr/{char_id}/hit/{{:04d}}.png", 13, 0),
                cls.STATE_DEAD: AnimatedSprite.anim_from_path_template(f"chr/{char_id}/death/{{:04d}}.png", 36, 0),
            }
        else:
            raise ValueError(f"Unknown character id: {char_id}")
        return animations


    def change_state(self, new_state):
        if self.state == new_state:
            return
        self.state = new_state
        self.state_timer = 0.0
        self.frame_index = 0
        self.blocking = False
        self.already_block_dmg = False
        self.hitbox = None
        self.frame_time = self.orig_frame_time
        self.play_animation(new_state)
        # immediate effects

        if new_state != self.STATE_WALK:
            self.vel.x = 0

    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key in self.input_map.values():
                action = list(self.input_map.keys())[list(self.input_map.values()).index(event.key)]
                self.input_states[action] = True
        elif event.type == pygame.KEYUP:
            if event.key in self.input_map.values():
                action = list(self.input_map.keys())[list(self.input_map.values()).index(event.key)]
                self.input_states[action] = False


    def receive_hit(self, damage, knockback=0):
        knockback *= CHAR_CONFIG[self.char_id]["knockback_multiplier"]
        if self.state == self.STATE_HIT or self.state == self.STATE_DEAD:
            return
        if self.invulnerable_timer > 0 :
            return
        if self.blocking:
            if self.already_block_dmg:
                return
            self.health -= damage // CHAR_CONFIG[self.char_id]["block_damage_divider"]
            knockback *= 0.4
            self.already_block_dmg = True
        else:
            self.health -= damage
            self.change_state(self.STATE_HIT)
        if self.health <= 0:
            self.health = 0
            self.change_state(self.STATE_DEAD)
            self.vel = pygame.math.Vector2(0, 0)
            return
        # apply knockback and hit state
        self.knockback_x -= knockback*self.facing

    def update(self, dt):
        """Update physics and state machine. dt is seconds elapsed."""

        # invulnerability timer
        if self.invulnerable_timer > 0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)

        self.stamina_timer += dt
        if self.stamina_timer >= self.stamina_period:
            self.stamina_timer -= self.stamina_period
            self.stamina = min(self.stamina + 1, 20)

        wanna_walk = self.input_states["left"] or self.input_states["right"]

        if self.state in (self.STATE_IDLE, self.STATE_WALK):
            if self.input_states["punch"] and self.has_stamina_for("punch"):
                self.change_state(self.STATE_PUNCH)
                self.stamina -= CHAR_CONFIG[self.char_id]["punch_stamina"]
            elif self.input_states["kick"] and self.has_stamina_for("kick"):
                self.change_state(self.STATE_KICK)
                self.stamina -= CHAR_CONFIG[self.char_id]["kick_stamina"]
            elif self.input_states["block"] and self.has_stamina_for("block"):
                self.change_state(self.STATE_BLOCK)
                self.stamina -= CHAR_CONFIG[self.char_id]["block_stamina"]
            else:
                if wanna_walk and self.state == self.STATE_IDLE:
                    self.change_state(self.STATE_WALK)
                elif self.state == self.STATE_WALK:
                    if not wanna_walk:
                        self.change_state(self.STATE_IDLE)
                    elif self.input_states["left"]:
                        self.vel.x = -self.walk_speed
                    elif self.input_states["right"]:
                        self.vel.x = self.walk_speed
        elif self.state in (self.STATE_KICK, self.STATE_PUNCH, self.STATE_BLOCK):
            if self.looped_times > 0:
                self.change_state(self.STATE_WALK if wanna_walk else self.STATE_IDLE)
            else:
                action_start = CHAR_CONFIG[self.char_id][f"{self.state}_start_frame"]
                action_end = CHAR_CONFIG[self.char_id][f"{self.state}_end_frame"]
                action_on = bool(self.frame_index >= action_start and self.frame_index < action_end)
                if self.state in (self.STATE_KICK, self.STATE_PUNCH):
                    # is attack
                    if action_on:
                        self.hitbox = self.get_attack_hitbox()
                        self.hit_damage = CHAR_CONFIG[self.char_id][f"{self.state}_dmg"]
                    else:
                        self.hitbox = None
                else:
                    #must be blocking
                    hold_frame = CHAR_CONFIG[self.char_id]["block_hold_frame"]
                    if self.frame_index >= hold_frame and self.input_states["block"]:
                        self.frame_index = hold_frame
                        self.frame_time = 10000
                    else:
                        self.frame_time = self.orig_frame_time
                    self.blocking = action_on
        elif self.state == self.STATE_HIT:
            if self.looped_times > 0:
                self.change_state(self.STATE_WALK if wanna_walk else self.STATE_IDLE)
        elif self.state == self.STATE_DEAD:
            self.loops = 0

        self.pos += self.vel * dt

        if self.knockback_x != 0:
            self.pos.x += self.knockback_x * dt
            self.knockback_x = max(0.0, self.knockback_x - 50.0 * (-1 if self.knockback_x < 0 else 1) * dt)

        # force MIN_X and MAX_X
        if self.pos.x < self.MIN_X:
            self.pos.x = self.MIN_X
        if self.pos.x > self.MAX_X:
            self.pos.x = self.MAX_X

        # update rect
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

        # advance timers
        self.state_timer += dt

        # update graphics
        self.flip_x = (self.facing == -1)
        if self.invulnerable_timer > 0:
            # apply flashing effect
            if int(self.state_timer * 10) % 2 == 0:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)

        super().update(dt)

    def get_attack_hitbox(self):
        start_x = CHAR_CONFIG[self.char_id][f"{self.state}_start_x"]
        end_x = CHAR_CONFIG[self.char_id][f"{self.state}_end_x"]
        hitbox = self.rect.copy()
        half_width = hitbox.width // 2
        hitbox_w_f = start_x + end_x
        hitbox.w = hitbox_w_f * half_width

        if self.facing == 1:
            hitbox.left = self.rect.centerx + start_x * half_width
        else:
            hitbox.right = self.rect.centerx - start_x * half_width

        return hitbox

    def has_stamina_for(self, action: str) -> bool:
        # placeholder, always return true for now
        return True

    def draw(self, surface, cam_pos):
        super().draw(surface, cam_pos)
        cam_offset = self.calc_cam_offset(cam_pos)
        if DBG_COLL:
            pygame.draw.rect(surface, pygame.Color("red" if not self.blocking else "blue"), self.rect.move(cam_offset), 2)
            if self.hitbox:
                pygame.draw.rect(surface, pygame.Color("green"), self.hitbox.move(cam_offset), 2)

    def reset(self):
        self.change_state(self.STATE_IDLE)
        self.pos = pygame.math.Vector2(self.start_pos)
        self.vel = pygame.math.Vector2(0, 0)
        self.size = pygame.Rect(0, 0, LittleGuy.DIM_X, LittleGuy.DIM_Y)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size.width, self.size.height)
        offset_naive = self.calc_offset_center()
        self.offset = offset_naive - pygame.math.Vector2(0, 50)

        # gameplay
        self.health = 100
        self.stamina = 20
        self.stamina_timer = 0.0
        self.stamina_period = 0.5
        self.invulnerable_timer = 0.0
        self.knockback_x = 0.0
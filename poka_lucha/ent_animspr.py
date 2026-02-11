from .entity import Entity
import pygame
from .resload import get_resource
import sys

DEBUG_ANIMSPR = '--debug' in sys.argv or '--debug-animspr' in sys.argv

class AnimatedSprite(Entity):
    def __init__(self, pos, animations, **kwargs):
        super().__init__(pos)
        self.animations = animations
        self.current_animation = None
        self.frame_index = 0
        self.frame_time = 1.0/15.0
        self.anim_frame_timer = 0.0
        self.flip_x = False
        self.flip_y = False
        self.offset = pygame.math.Vector2(0, 0)
        self.looped_times = 0
        self.loops = -1

        if DEBUG_ANIMSPR:
            self.font = pygame.font.Font(None, 24)

        if "initial" in kwargs:
            self.play_animation(kwargs["initial"])
            self.size = self.animations[self.current_animation]["frames"][0].get_size()

    @staticmethod
    def cut_spritesheet(sheet, sprite_width, sprite_height, max_count:int = -1):
        """Cut a spritesheet into individual sprites."""
        sprites = []
        sheet_width, sheet_height = sheet.get_size()
        for y in range(0, sheet_height, sprite_height):
            for x in range(0, sheet_width, sprite_width):
                rect = pygame.Rect(x, y, sprite_width, sprite_height)
                sprite = sheet.subsurface(rect)
                sprites.append(sprite)
        if max_count > 0:
            return sprites[:max_count]
        return sprites

    @staticmethod
    def anim_from_path_template(path_template:str, frame_count:int, from_index=1, frame_time:float = 1.0/12.0):
        """Create an animation from a path template."""
        frames = []
        for i in range(from_index, from_index + frame_count):
            frame_path = path_template.format(i)
            frame = get_resource(frame_path)
            frames.append(frame)
        return {
                "frames": frames,
                "frame_time": frame_time
            }

    def play_animation(self, name, loops = -1):
        if self.current_animation != name:
            self.current_animation = name
            self.frame_index = 0
            self.anim_frame_timer = 0.0
            self.looped_times = 0
            self.loops = loops

    def update(self, dt):
        if self.current_animation:
            self.anim_frame_timer += dt
            if self.anim_frame_timer >= self.frame_time:
                self.frame_index += 1
                self.anim_frame_timer = 0.0
                could_loop = self.loops == -1 or (self.looped_times < self.loops)
                if self.frame_index >= len(self.animations[self.current_animation]["frames"]):
                    if could_loop:
                        self.frame_index = 0
                        self.looped_times += 1
                    else:
                        self.frame_index = len(self.animations[self.current_animation]["frames"]) - 1

    def draw(self, surface, cam_pos):
        if self.current_animation:
            cam_offset = self.calc_cam_offset(cam_pos)
            frame = self.animations[self.current_animation]["frames"][self.frame_index]
            if self.flip_x or self.flip_y:
                frame = pygame.transform.flip(frame, self.flip_x, self.flip_y)
            surface.blit(frame, self.rect.topleft + self.offset + cam_offset)
            if DEBUG_ANIMSPR:
                text = f"Anim: {self.current_animation}, Frame: {self.frame_index}"
                # Render the debug text (you'll need a font and surface for this)
                debug_surface = pygame.Surface((200, 50))
                debug_surface.fill((0, 0, 0))
                text_surface = self.font.render(text, True, (255, 255, 255))
                debug_surface.blit(text_surface, (5, 5))
                surface.blit(debug_surface, self.rect.topleft + cam_offset)

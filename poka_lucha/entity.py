import pygame
from typing import Optional, Tuple

pygame.init()


class Entity(pygame.sprite.Sprite):
    """
    Simple base class for game entities.
    - Uses pygame.sprite.Sprite so it integrates with Groups.
    - Keeps float position/velocity using Vector2.
    - update(dt) expects dt in seconds.
    """

    def __init__(
        self,
        pos: Tuple[float, float] = (0, 0),
        image: Optional[pygame.Surface] = None,
        size: Tuple[int, int] = (32, 32),
        group: pygame.sprite.AbstractGroup = None
    ):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)      # precise position (floats)
        self.vel = pygame.math.Vector2(0, 0)     # velocity (pixels/sec)
        self.acc = pygame.math.Vector2(0, 0)     # acceleration (pixels/sec^2)
        self.scroll = True                       # whether affected by camera scroll, false for hud stuff or static bg
        self.parallax = 1.0                      # parallax factor (1.0 = no parallax)

        self.angle = 0.0                         # degrees
        self.angular_velocity = 0.0              # degrees/sec

        # image and rect required by pygame.sprite.Sprite
        if image is not None:
            self._orig_image = image.convert_alpha()
        else:
            self._orig_image = pygame.Surface(size, pygame.SRCALPHA)
        self.image = self._orig_image.copy()
        self.rect = self.image.get_rect(topleft=self.pos)

        self.alive_flag = True

        if group is not None:
            group.add(self)

    def calc_cam_offset(self, cam_pos: pygame.math.Vector2) -> pygame.math.Vector2:
        """Calculate the camera offset for this entity."""
        m_cam_pos = -cam_pos
        return pygame.math.Vector2(m_cam_pos.x * self.parallax, m_cam_pos.y * self.parallax) if self.scroll else pygame.math.Vector2(0, 0)

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        """
        Update physics and transform.
        dt: time delta in seconds.
        """
        # basic Euler integration
        self.vel += self.acc * dt
        self.pos += self.vel * dt

        # rotation (keep original image and rotate from it)
        self.angle = (self.angle + self.angular_velocity * dt) % 360
        if self.angle:
            self.image = pygame.transform.rotate(self._orig_image, -self.angle)
            # keep sprite centered at self.pos when rotated
            self.rect = self.image.get_rect(center=self.pos)
        else:
            self.image = self._orig_image
            self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface: pygame.Surface, cam_pos: pygame.math.Vector2):
        """Blit the entity to the given surface."""
        cam_off = self.calc_cam_offset(cam_pos)
        surface.blit(self.image, self.rect.move(cam_off.x, cam_off.y))

    # convenience helpers
    def apply_impulse(self, impulse: Tuple[float, float]):
        """Add immediate velocity (impulse is treated as pixels/sec)."""
        self.vel += pygame.math.Vector2(impulse)

    def set_position(self, pos: Tuple[float, float]):
        self.pos = pygame.math.Vector2(pos)
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def on_collision(self, other: "Entity"):
        """Override in subclasses to handle collisions."""
        pass

    def remove(self):
        """Mark dead and remove from all groups."""
        self.alive_flag = False
        super().kill()
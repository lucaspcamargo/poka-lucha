from typing import Tuple
from .entity import Entity
import pygame

class Bar(Entity):

    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        color: pygame.Color = pygame.Color("green"),
        bg_color: pygame.Color = pygame.Color("red"),
        max_value: float = 100.0,
        current_value: float = 100.0,
        ltr: bool = False,
        group: pygame.sprite.AbstractGroup = None
    ):
        super().__init__(pos, size=size, group=group)
        self.color = color
        self.bg_color = bg_color
        self.max_value = max_value
        self.current_value = current_value
        self.rect = pygame.Rect(pos, size)
        self.image = pygame.Surface(self.rect.size)
        self.scroll = False
        self.ltr = ltr

    def set_value(self, value: float):
        """Set the current value of the bar."""
        self.current_value = max(0, min(self.max_value, value))

    def update(self, dt: float = 0):
        """Update the bar's visual representation."""
        super().update(dt)
        fill_ratio = self.current_value / self.max_value if self.max_value > 0 else 0
        fill_width = int(self.rect.width * fill_ratio)

        # Create a new surface for the bar
        self.image.fill(self.bg_color)
        if fill_width > 0:
            pygame.draw.rect(self.image, self.color, (self.rect.width - fill_width, 0, fill_width, self.rect.height) if self.ltr else (0, 0, fill_width, self.rect.height))
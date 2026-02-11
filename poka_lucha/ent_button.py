from typing import Callable, Optional, Tuple
import pygame
from .entity import Entity

# ent_button.py



class Button(Entity):
    """
    A simple clickable button Entity.
    - rect: pygame.Rect or (x, y, w, h)
    - text: label text
    - callback: function(button: Button) called on click
    """

    def __init__(
        self,
        x: int,
        y: int,
        image: Optional[pygame.Surface] = None,
        text: str = "",
        callback: Optional[Callable] = None,
        font: Optional[pygame.font.Font] = None,
        enabled: bool = True,
        visible: bool = True,
    ):
        # Attempt to call parent initializer if available
        try:
            super().__init__()
        except TypeError:
            # If Entity requires different signature, it's okay to continue;
            # keep Button lightweight and self-contained.
            pass

        self.image = image

        self.rect = pygame.Rect(x, y, 200, 50)
        if self.image:
            self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())
        self.text = text
        self.callback = callback

        pygame.font.init()
        self.font = font or pygame.font.SysFont(None, 20)

        self.enabled = enabled
        self.visible = visible

        # internal state
        self.hover = False
        self.pressed = False
        self._mouse_down_inside = False

    def update(self, dt: float = 0):
        pass

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events. Returns True if the event was consumed.
        """
        
        if not self.visible or not self.enabled:
            # still track hover for visual consistency on motion if visible
            if event.type == pygame.MOUSEMOTION and self.visible:
                self.hover = self.rect.collidepoint(event.pos)
            return False

        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                self._mouse_down_inside = True
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed:
                self.pressed = False
                consumed = False
                if self._mouse_down_inside and self.rect.collidepoint(event.pos):
                    consumed = True
                    if self.callback:
                        self.callback()
                self._mouse_down_inside = False
                return consumed

        return False

    def draw(self, surface: pygame.Surface, _cam_pos):
        """
        Draw the button onto the provided surface.
        """
        if not self.visible:
            return

        if self.image:
            surface.blit(self.image, self.rect)

        if self.text:
            text_surf = self.font.render(self.text, True, (10, 10, 10))
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    # convenience setters/getters
    def set_callback(self, cb: Optional[Callable[["Button"], None]]):
        self.callback = cb

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if not enabled:
            self.hover = False
            self.pressed = False

    def set_visible(self, visible: bool):
        self.visible = visible

    def is_hovered(self) -> bool:
        return self.hover

    def is_pressed(self) -> bool:
        return self.pressed
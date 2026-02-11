from __future__ import annotations
from typing import Any, Dict, Optional
import abc
import pygame

class Scene(abc.ABC):
    """
    Base class for a game scene.

    Usage:
      - subclass and implement update()
      - override init() / teardown() to allocate / free resources
      - optionally override handle_event() and render()
    """

    def __init__(self, name: Optional[str] = None, manager: Any = None) -> None:
        self.name = name or self.__class__.__name__
        self.manager = manager  # optional scene manager / game reference
        self.active = False
        self.paused = False
        self.resources: Dict[str, Any] = {}
        self.width = manager.width
        self.height = manager.height
        self.entities = []
        self.cam_min = pygame.math.Vector2(0, 0)
        self.cam_max = pygame.math.Vector2(0, 0)
        self.cam_pos = pygame.math.Vector2(0, 0)

    def enter(self) -> None:
        """
        Called when the scene is started/activated.
        Override to allocate resources, start music, spawn entities, etc.
        """
        self.active = True

    def exit(self) -> None:
        """
        Called when the scene is stopped/removed.
        Override to free resources, stop sounds, cancel timers, etc.
        Default implementation clears stored resources.
        """
        self.active = False
        self.resources.clear()

    @abc.abstractmethod
    def update(self, dt: float) -> None:
        for ent in self.entities:
            if ent is None:
                continue
            # prefer custom update(dt)
            update_fn = getattr(ent, "update", None)
            if callable(update_fn):
                update_fn(dt)

    def handle_event(self, event: Any) -> None:
        for ent in self.entities:
            if ent is None:
                continue
            # prefer custom handle_event(event)
            handle_fn = getattr(ent, "handle_event", None)
            if callable(handle_fn):
                handle_fn(event)

    def render(self, surface: Any) -> None:
        """Render entities. Entities may implement render(surface), draw(surface), or have image/rect."""
        # render in order of z attribute if present
        entities = sorted(self.entities, key=lambda e: getattr(e, "z", 0))
        for ent in entities:
            if ent is None:
                continue
            # prefer custom draw(surface, cam_pos)
            draw_fn = getattr(ent, "draw", None)
            if callable(draw_fn):
                draw_fn(surface, self.cam_pos)
            elif hasattr(ent, "image") and hasattr(ent, "rect"):
                surface.blit(ent.image, ent.rect)

    def pause(self) -> None:
        """Pause the scene's updates (update should typically early-return when paused)."""
        self.paused = True

    def resume(self) -> None:
        """Resume updates."""
        self.paused = False
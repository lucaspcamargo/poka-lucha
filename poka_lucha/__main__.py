#!/usr/bin/env python3
from .game_main import Game
import pygame
import os, sys

def main():
    try:
        game = Game()
        game.run()
    except:
        import traceback as tb
        tb.print_exc
        raise
    finally:
        pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    os.environ["PYGAME_BLEND_ALPHA_SDL2"] = "1"
    main()
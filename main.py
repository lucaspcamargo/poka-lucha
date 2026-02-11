# /// script
# dependencies = ["pygame-ce"]
# ///

# This is the main file for pygbag, the web version
# for the desktop version, run the game package as in:
# $ python -m pygametest

from poka_lucha.game_main import Game
import asyncio, os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
os.environ["PYGAME_BLEND_ALPHA_SDL2"] = "1"

async def main():
    game = Game(is_web = True)
    await game.run_async()

asyncio.run(main())
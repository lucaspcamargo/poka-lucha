import pygame
from .resload import get_resource

def play_sfx(sound_file: str):
    """Play a sound effect."""
    snd = get_resource(sound_file)
    if snd is not None:
        snd.play()
    else:
        print(f"Failed to load sound effect: {sound_file}")

from typing import Any, Optional
import time
import pygame
from . import resload

"""
pygametest.music - simple BGM helper using resload to fetch music resources.

Provides:
- play(id, loops=-1, fade_ms=0, start_pos=0.0)
- pause()
- resume()
- stop(fade_ms=0)
- fadeout(ms)
- set_bgm_volume(vol)
- get_bgm_volume()

This module will try to use pygame.mixer.music for filename/streaming resources
and pygame.mixer.Sound + Channel for preloaded Sound objects returned by resload.
"""


RES_DIR = "./res/"

# internal state
_current_id: Optional[str] = None
_current_res: Optional[Any] = None
_current_type: Optional[str] = None  # 'music' or 'sound'
_current_channel: Optional[pygame.mixer.Channel] = None
_loop_id: Optional[str] = None   # set when using play_with_intro
_paused: bool = False
_bgm_volume: float = 1.0


def _ensure_mixer():
    if not pygame.mixer.get_init():
        # Basic init; user project can initialize with custom params before calling.
        pygame.mixer.init()


def _get_resource(identifier: str):
    ret = resload.get_resource(identifier)
    #if ret is None:
    #    raise RuntimeError(f"Music resource '{identifier}' not found via resload.")
    return ret


def _clear_state():
    global _current_id, _current_res, _current_type, _current_channel, _loop_id, _paused
    _current_id = None
    _current_res = None
    _current_type = None
    _current_channel = None
    _loop_id = None
    _paused = False


def play(identifier: str, loops: int = -1, fade_ms: int = 0, start_pos: float = 0.0):
    """
    Play background music identified by `identifier` via resload.
    loops: -1 for infinite (music semantics). For Sound objects, loops works similarly.
    fade_ms: fade-in milliseconds
    start_pos: only used for pygame.mixer.music.play (position in seconds)
    """
    global _current_id, _current_res, _current_type, _current_channel, _paused, _bgm_volume

    _ensure_mixer()

    resource = _get_resource(identifier)
    _current_id = identifier
    _current_res = resource
    _paused = False
    _current_channel = None
    _current_type = None

    # If resource is a path/filename or file-like, use pygame.mixer.music (streaming)
    if isinstance(resource, str) or hasattr(resource, "read"):
        try:
            pygame.mixer.music.load(resource)
            pygame.mixer.music.set_volume(_bgm_volume)
            # pygame.mixer.music.play(loops, start, fade_ms)
            pygame.mixer.music.play(loops=loops, start=start_pos, fade_ms=fade_ms)
            _current_type = "music"
            return
        except Exception:
            # fallthrough to try treating as Sound if possible
            pass

    # If resource is a Sound instance, play it on a channel to allow pause/resume.
    if isinstance(resource, pygame.mixer.Sound):
        resource.set_volume(_bgm_volume)
        ch = resource.play(loops=loops, fade_ms=fade_ms)
        _current_channel = ch
        _current_type = "sound"
        return

    print("NO MUSIC?")
    return

    # If we couldn't handle the resource, raise
    raise RuntimeError(f"Unsupported music resource type returned for '{identifier}': {type(resource)}")


def play_with_intro(intro_id: str, loop_id: str, fade_ms: int = 0):
    """
    Play intro_id once, then loop loop_id seamlessly and infinitely.
    Both identifiers are resload keys (e.g. "bgm/intro.ogg", "bgm/loop.ogg").
    """
    global _current_id, _current_type, _loop_id, _paused, _bgm_volume

    _ensure_mixer()
    stop()

    intro_path = RES_DIR + intro_id
    loop_path  = RES_DIR + loop_id

    pygame.mixer.music.load(intro_path)
    pygame.mixer.music.set_volume(_bgm_volume)
    pygame.mixer.music.play(loops=0, fade_ms=fade_ms)
    pygame.mixer.music.queue(loop_path, loops=-1)

    _current_id   = intro_id
    _current_type = "music"
    _loop_id      = loop_id
    _paused       = False


def pause():
    """Pause currently playing music (works for streaming music and Sound channel)."""
    global _paused
    if _current_type == "music":
        try:
            pygame.mixer.music.pause()
            _paused = True
        except Exception:
            pass
    elif _current_type == "sound" and _current_channel is not None:
        try:
            _current_channel.pause()
            _paused = True
        except Exception:
            pass


def resume():
    """Resume paused music."""
    global _paused
    if not _paused:
        return
    if _current_type == "music":
        try:
            pygame.mixer.music.unpause()
            _paused = False
        except Exception:
            pass
    elif _current_type == "sound" and _current_channel is not None:
        try:
            _current_channel.unpause()
            _paused = False
        except Exception:
            pass


def stop(fade_ms: int = 0):
    """
    Stop current music. If fade_ms > 0, will fade out over that many milliseconds.
    """
    if _current_type == "music":
        try:
            if fade_ms > 0:
                pygame.mixer.music.fadeout(fade_ms)
            else:
                pygame.mixer.music.stop()
        except Exception:
            pass
        finally:
            _clear_state()
    elif _current_type == "sound":
        try:
            if _current_channel is not None:
                if fade_ms > 0:
                    _current_channel.fadeout(fade_ms)
                else:
                    _current_channel.stop()
        except Exception:
            pass
        finally:
            _clear_state()
    else:
        _clear_state()


def fadeout(ms: int):
    """Convenience: fade out current music over ms milliseconds."""
    stop(fade_ms=ms)


def set_bgm_volume(vol: float):
    """
    Set global BGM volume (0.0 to 1.0).
    Applies immediately to the currently playing resource if any.
    """
    global _bgm_volume
    vol = max(0.0, min(1.0, float(vol)))
    _bgm_volume = vol
    try:
        if _current_type == "music":
            pygame.mixer.music.set_volume(_bgm_volume)
        elif _current_type == "sound" and isinstance(_current_res, pygame.mixer.Sound):
            _current_res.set_volume(_bgm_volume)
        else:
            # nothing playing yet; volume is stored for future play()
            pass
    except Exception:
        pass


def get_bgm_volume() -> float:
    """Return current BGM volume (0.0 - 1.0)."""
    return _bgm_volume


def is_playing() -> bool:
    """Return True if music or tracked Sound channel is currently playing (not paused)."""
    if _current_type == "music":
        try:
            return pygame.mixer.music.get_busy()
        except Exception:
            return False
    elif _current_type == "sound" and _current_channel is not None:
        try:
            return _current_channel.get_busy()
        except Exception:
            return False
    return False
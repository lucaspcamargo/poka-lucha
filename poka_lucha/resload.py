import os
from pathlib import Path
import pygame

# utility to load all files from the resources directory
# glob all files in resource directory and load according to file extension
# loads images as surfaces, sounds as Sound objects, and fonts as Font objects

# resource registry: keys are paths relative to ./res/ using forward slashes
RESOURCES = {}

# file type groups
_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tga", ".webp"}
_SOUND_EXTS = {".wav", ".ogg", ".mp3", ".flac"}
_FONT_EXTS = {".ttf", ".otf"}


def _ensure_pygame_modules():
    # initialize font and mixer modules if necessary; ignore failures (headless environments)
    try:
        if not pygame.get_init():
            pygame.init()
    except Exception:
        pass
    try:
        if not pygame.font.get_init():
            pygame.font.init()
    except Exception:
        pass
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except Exception:
        pass


def load_resources_init(res_dir: Path | str | None = None) -> list[Path]:
    """
    Return a list of file Paths under res_dir that should be loaded.
    Does not modify RESOURCES or perform any pygame loading.
    """
    if res_dir is None:
        res_dir = Path(__file__).parent / "res"
    res_dir = Path(res_dir)

    if not res_dir.exists():
        return []

    files = [p for p in res_dir.rglob("*") if p.is_file()]
    # deterministic order
    files.sort(key=lambda p: p.as_posix())
    return files


def load_resource(path: Path | str, res_dir: Path | str | None = None):
    """
    Load a single file and store it in the global RESOURCES dict.
    Returns the loaded resource (Surface, Sound, Font, bytes, or None).
    If res_dir is provided it is used to compute the resource key (relative path).
    """
    global RESOURCES
    _ensure_pygame_modules()

    path = Path(path)
    if res_dir is None:
        res_dir = Path(__file__).parent / "res"
    res_dir = Path(res_dir)

    try:
        # compute key relative to res_dir if possible, otherwise use posix path
        try:
            key = path.relative_to(res_dir).as_posix()
        except Exception:
            key = path.as_posix()

        ext = path.suffix.lower()

        if ext in _IMAGE_EXTS:
            try:
                resource = pygame.image.load(str(path))
            except Exception:
                resource = path.read_bytes()
        elif ext in _SOUND_EXTS:
            try:
                resource = pygame.mixer.Sound(str(path))
            except Exception:
                resource = path.read_bytes()
        elif ext in _FONT_EXTS:
            try:
                resource = pygame.font.Font(str(path), 16)
            except Exception:
                resource = path.read_bytes()
        else:
            resource = path.read_bytes()
    except Exception:
        try:
            resource = path.read_bytes()
        except Exception:
            resource = None

    RESOURCES[key] = resource
    return resource


def load_resources(res_dir: Path | str | None = None) -> dict:
    """
    Clear and load all resources under res_dir into the global RESOURCES dict.
    Uses load_resources_init to gather files and load_resource to load each file.
    """
    global RESOURCES
    RESOURCES.clear()

    files = load_resources_init(res_dir)
    for p in files:
        load_resource(p, res_dir)

    return RESOURCES


def get_resource(key: str, default=None):
    """Return a loaded resource by its relative-res key."""
    return RESOURCES.get(key, default)


def reload_resources(res_dir: Path | str | None = None):
    """Clear and reload resources from disk."""
    return load_resources(res_dir)
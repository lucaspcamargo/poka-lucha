
import sys
import pygame

from pygametest.scene_title import SceneTitle
from pygametest.scene_victory import SceneVictory

from .resload import load_resources_init, load_resource

from .scene_gameplay import SceneGameplay


WIDTH, HEIGHT = 1920, 1080
TITLE = "Poca Lucha"
RES_DIR = "./res/"
FULLSCREEN = (sys.argv.count("--fullscreen") + sys.argv.count("-f")> 0)
SHOW_FPS = "--debug" in sys.argv or "--fps" in sys.argv

class Game:
    def __init__(self, width: int = WIDTH, height: int = HEIGHT, is_web: bool = False):
        pygame.init()
        self.width = width
        self.height = height
        if is_web:
            self.screen = pygame.display.set_mode((self.width, self.height))
            
        else:
            flags = pygame.SCALED | pygame.RESIZABLE
            if FULLSCREEN:
                flags |= pygame.FULLSCREEN
            self.screen = pygame.display.set_mode((self.width, self.height), flags, vsync=1)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.dbg_font = pygame.font.Font(None, 32)
        self.bg_color = pygame.Color("black")

        self.scene = None
        if("-g" in sys.argv):
            self.next_scene = SceneGameplay(self)
        elif("-v" in sys.argv):
            self.next_scene = SceneVictory(0, self)
        else:
            self.next_scene = SceneTitle(self)

    def run(self):
        import asyncio
        asyncio.get_event_loop().run_until_complete(self.resource_load())

        while self.running:
            dt = self.clock.tick() / 1000.0  # delta time in seconds
            if self.next_scene:
                if self.scene:
                    self.scene.exit()
                self.scene = self.next_scene
                self.scene.enter()
                self.next_scene = None
            if self.scene:
                self.scene.update(dt)
                self.scene.render(self.screen)

            self.handle_events()
            self.update(dt)
            self.draw()

    async def run_async(self):
        import asyncio
        await self.resource_load()
        while self.running:
            dt = self.clock.tick() / 1000.0  # delta time in seconds
            await asyncio.sleep(0)
            if self.next_scene:
                if self.scene:
                    self.scene.exit()
                self.scene = self.next_scene
                self.scene.enter()
                self.next_scene = None
            if self.scene:
                self.scene.update(dt)
                self.scene.render(self.screen)

            self.handle_events()
            self.update(dt)
            self.draw()
        await asyncio.sleep(0)

    async def resource_load(self):
        import asyncio
        load_color = pygame.Color("yellow")
        load_bg_color = pygame.Color("#222222")
        files = load_resources_init(RES_DIR)
        total = len(files)
        done = 0
        last_frame = pygame.time.get_ticks()
        for p in files:
            load_resource(p, RES_DIR)
            done += 1
            print(f"Loaded {done}/{total}: {p}")
            if pygame.time.get_ticks() - last_frame > 50:
                last_frame = pygame.time.get_ticks()
                self.screen.fill(self.bg_color)
                pygame.draw.rect(self.screen, load_bg_color, pygame.Rect(50, self.height // 2 - 15, self.width - 100, 30))
                pygame.draw.rect(self.screen, load_color, pygame.Rect(50, self.height // 2 - 15, int((done / total) * (self.width - 100)), 30))
                pygame.display.flip()
                await asyncio.sleep(0)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        
            self.scene.handle_event(event) if self.scene else None

    def update(self, dt: float):
        self.scene.update(dt) if self.scene else None

    def draw(self):
        if SHOW_FPS:
            fps_text = self.dbg_font.render(f"FPS: {self.clock.get_fps():.1f}", False, pygame.Color("green"), pygame.Color("black"))
            rect = fps_text.get_rect()
            sw, sh = self.screen.get_size()
            self.screen.blit(fps_text, (40, sh - rect.height - 40))  # fixed x pos for FPS display

        pygame.display.flip()

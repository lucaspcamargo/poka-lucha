# A particle system entity type

import pygame
from poka_lucha.entity import Entity

class ParticleSystem(Entity):
    def __init__(self, emit_rate=10, particle_lifetime=3.0, particle_color=(255, 255, 255), particle_size=5, affectors=[]):
        super().__init__((0.0, 0.0))
        self.emit_rate = emit_rate
        self.particle_lifetime = particle_lifetime
        self.particle_color = particle_color
        self.particle_size = particle_size
        self.particles = []
        self.affectors = affectors
        self.time_since_emit = 0.0

    def update(self, dt):
        # Emit new particles based on the emit rate
        if self.emit_rate > 0.0:
            self.time_since_emit += dt
            while self.time_since_emit > 1.0 / self.emit_rate:
                self.time_since_emit -= 1.0 / self.emit_rate
                self.emit_particle()

        # Update existing particles and remove expired ones
        for particle in self.particles[:]:
            particle['lifetime'] -= dt
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
            else:
                # Simple movement (e.g., upward)
                particle['pos'] = (
                    particle['pos'][0] + particle['vel'][0] * dt,
                    particle['pos'][1] + particle['vel'][1] * dt,
                )
        for affector in self.affectors:
            affector(self.particles, dt)

    def emit_particle(self, pos = (0,0,), vel=(0,0,)):
        pass
        # Create a new particle with initial properties
        particle = {
            'pos': pos or (0, 0),  # Start at the emitter's position
            'lifetime': self.particle_lifetime,
            'color': self.particle_color,
            'size': self.particle_size,
            'vel': vel or (0,0,),
        }
        self.particles.append(particle)

    def draw(self, surface, cam_pos = None):
        for particle in self.particles:
            pygame.draw.circle(surface, particle['color'], (int(particle['pos'][0]), int(particle['pos'][1])), round(particle['size']))

import logging
import os
import random
import sys

from src.camera import Camera

import pygame
from pygame import sprite
from pygame.locals import *
from src.const import *
from src.game_objects.ground import Ground
from src.game_objects.player import Player


class Game:
    
    def __init__(self):
        # Initializing Pygame window
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.display.set_caption(CAPTION)
        self.surface = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), 0, 32)
        logging.basicConfig(level=LOG_LEVEL,
                            datefmt='%m/%d/%Y %I:%M:%S%p',
                            format='%(asctime)s %(message)s')

        self.test_level()

    def test_level(self):
        self.entities = {ALL_ENTITIES: sprite.Group(), WORLD_1: {ALL_ENTITIES: sprite.Group()},
                         WORLD_2: {ALL_ENTITIES: sprite.Group()}, BOTH_WORLDS: {ALL_ENTITIES: sprite.Group()}}
        self.fps_clock = pygame.time.Clock()
        self.events = pygame.event.get()
        screen = pygame.Rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)
        self.camera = Camera(screen)
        self.world = WORLD_1

        player = Player(self, pos=(200, 200))
        self.add_entity(player)
        for i in range(7):
            ground = Ground(self, pos=(i * Ground.width + Ground.width / 2,
                                       DISPLAY_HEIGHT - Ground.height / 3))
            self.add_entity(ground)
            if i == 4:
                ground = Ground(self, pos=(i * Ground.width + Ground.width / 2,
                                           DISPLAY_HEIGHT - Ground.height * 4 / 3))
                self.add_entity(ground, WORLD_2)
        self.background_color = PALETTE_D_GREEN
        self.run()

    def run(self):
        running = True
        while running:
            self.surface.fill(self.background_color)
            if pygame.event.peek(pygame.QUIT):
                running = False
            self.events = pygame.event.get()
            self.update_all_sprites()
            self.draw_all_sprites()

            pygame.display.update()
            self.fps_clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def update_all_sprites(self):
        for x in self.entities[ALL_ENTITIES]:
            x.update()
    
    def draw_all_sprites(self):
        current_world = self.world
        if current_world == WORLD_1:
            passive_world = WORLD_2
        else:
            passive_world = WORLD_1
        active_entities = self.entities[current_world][ALL_ENTITIES].sprites()
        active_entities += self.entities[BOTH_WORLDS][ALL_ENTITIES].sprites()
        active_entities.sort(key=lambda x: x.depth, reverse=True)
        passive_entities = self.entities[passive_world][ALL_ENTITIES].sprites()
        passive_entities.sort(key=lambda x: x.depth, reverse=True)
        total_entities = passive_entities + active_entities
        # Draw based on depth
        for entity in total_entities:
            entity.draw()
    
    def add_entity(self, entity, world=BOTH_WORLDS):
        # Add entity to class's sprite group
        class_name = entity.__class__.__name__
        if class_name not in self.entities[world]:
            self.entities[world][class_name] = sprite.Group()
        self.entities[world][class_name].add(entity)
        logging.info(f"{entity} created in {world}")
        
        # Also add to global entity groups
        self.entities[world][ALL_ENTITIES].add(entity)
        self.entities[ALL_ENTITIES].add(entity)
        entity.set_color(world)

    def warp_world(self):
        if self.world == WORLD_1:
            old_world = WORLD_1
            self.world = WORLD_2
        else:
            old_world = WORLD_2
            self.world = WORLD_1
        for entity in self.entities[self.world][ALL_ENTITIES]:
            entity.change_color("Active")
        for entity in self.entities[old_world][ALL_ENTITIES]:
            entity.change_color("Passive")
        logging.info(f"Warped from {old_world} to {self.world}")

    def reset(self):
        self.test_level()

if __name__ == "__main__":
    Game()

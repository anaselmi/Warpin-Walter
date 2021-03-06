from src.const import *
from src.game_objects.dynamic.dumb_enemy import DumbEnemy
from src.game_objects.dynamic.player import Player
from src.game_objects.interactible.goal import Goal
from src.game_objects.interactible.warp_consumable import WarpCharge
from src.game_objects.terrain.background_block import BackgroundBlock
from src.game_objects.terrain.ground import Ground
from src.level.level import Level


class TutorialTwo(Level):
    
    def __init__(self, game):
        name = "Tight Hallway".title()
        super().__init__(game, name=name)
    
    def build(self):
        player = Player(self.game, pos=(200, 900), warp_charges=0)
        self.game.add_entity(player, "one")
        self.game.camera.follow(player)
        bottom_left_pos = (0, 1000)
        room_width = 22
        room_height = 6
    
        # Floor
        bottom_right_pos = build_row(Ground, self.game, bottom_left_pos, room_width)
    
        # Left Guard
        top_left_pos = build_column(Ground, self.game, bottom_left_pos, room_height, up=True)
        # Right Guard
        build_column(Ground, self.game, bottom_right_pos, room_height, up=True)
    
        # Ceiling
        top_right_pos = build_row(Ground, self.game, top_left_pos, room_width)
    
        # Background
        build_array(BackgroundBlock, self.game, top_left_pos, (room_width, room_height), world="three")
    
        # Ennemy
        spawn_pos = get_end_pos(Ground, bottom_left_pos, (8, 2), up=True)
        enemy = DumbEnemy(self.game, pos=spawn_pos)
        self.game.add_entity(enemy, "one")
    
        # Low ceiling
        _pos = get_end_pos(Ground, top_right_pos, (2, 2), left=True)
        end_pos = build_array(Ground, self.game, _pos, (room_width - 7, room_height-3), left=True)
    
        # warp charge
        pos = get_end_pos(Ground, end_pos, (2, 2))
        charge = WarpCharge(self.game, pos=pos)
        self.game.add_entity(charge)
    
        # goal
        pos = get_end_pos(Ground, bottom_right_pos, (2, 2), left=True, up=True)
        build_array(Goal, self.game, pos, (1, 1))
    
        # 2nd enemy
        enemy = DumbEnemy(self.game, pos=pos)
        self.game.add_entity(enemy, "one")
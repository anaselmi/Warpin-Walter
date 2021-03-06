import itertools
import logging

from src.const import *


class GameObject(pygame.sprite.Sprite):
    font = pygame.font.SysFont("monospace", 30)

    def __init__(self, game, *args,
                 pos, depth=0, image, world=None, is_solid=True, **kwargs):
        
        super().__init__()
        self.game = game
        self.x, self.y = pos
        self.depth = depth
        self.image = image
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y
        
        self.is_solid = is_solid
        self.world = world
        
        self.inactive_color = L_GREY
        
        self.font = GameObject.font

        self.ticks_per_frame = 1
        self._image_ticks = self.ticks_per_frame
        
    def update(self):
        # stay on one image for several ticks so you don't fffast!
        if self._image_ticks > 0:
            self._image_ticks -= 1
        else:
            try:
                self.image = next(self._images)
                self._frame_index += 1

            except Exception as e:
                logging.debug(e)
                
            self._image_ticks = self.ticks_per_frame
    
    def draw(self):
        if self.game.camera.rect.colliderect(self.rect):
            if self.world is not None and self.world != self.game.world:
                self.draw_inactive()
            else:
                self.draw_active()
            
            # Flashing
            if hasattr(self, "_flash_timer") and self._flash_timer > 0:
                if self._flash_timer % (2 * self._flash_period) in range(self._flash_period):
                    self.overlay_color(self._flash_color, alpha=self._flash_alpha)
                self._flash_timer -= 1
    
    def draw_active(self):
        adjusted = self.game.camera.adjust_rect(self.rect)
        scaled_image = pygame.transform.scale(self.image, adjusted.size)
        if hasattr(self, "x_dir"):
            scaled_image = pygame.transform.flip(scaled_image, self.x_dir == -1, 0)
        self.game.surface.blit(scaled_image, adjusted)
    
    def draw_inactive(self):
        self.overlay_color(self.inactive_color)
        
    def set_image(self, image_name):
        try:
            if not hasattr(self, "image_name") or image_name != self.image_name:
                self.image_name = image_name
                self._images = itertools.cycle(self.__class__.images[image_name])
                self.image = next(self._images)
                self._frame_index = 0
        except Exception as e:
            logging.debug(e)

    def overlay_color(self, color, alpha=255):
        adjusted = self.game.camera.adjust_rect(self.rect)
        scaled_image = pygame.transform.scale(self.image, adjusted.size)
        if hasattr(self, "x_dir"):
            scaled_image = pygame.transform.flip(scaled_image, self.x_dir == -1, 0)
        
        mask = pygame.mask.from_surface(scaled_image)
        outline = mask.outline()
        if not outline:
            outline = [(0,0),
                       (self.rect.w, 0),
                       (self.rect.w, self.rect.h),
                       (0, self.rect.h),
                       (0, 0)]

        mask_surf = pygame.Surface(adjusted.size)
        pygame.draw.polygon(mask_surf, color, outline, 0)
        mask_surf.set_colorkey((0, 0, 0))
        mask_surf.set_alpha(alpha)
        
        self.game.surface.blit(mask_surf, adjusted)
    
    def flash_color(self, color, ticks=10, period=3, alpha=255):
        self._flash_color = color
        self._flash_timer = ticks
        self._flash_period = period
        self._flash_alpha = alpha
    
    def collide_with(self, collidee, **conditions):
        """
        check collision with all instances of a class or specific instance
        :param collidee: Type(a class) or Sprite(an instance)
        :param conditions: dict: additional conditions to meet eg. {"rect.w": 100}
        :return: Sprite or None
        """
        
        # Check with all instance of a class
        if type(collidee) == type:
            for sprite in self.game.entities[ALL_SPRITES]:
                # Check if colliding and isinstance()
                if self.rect.colliderect(sprite.rect) and isinstance(sprite, collidee):
                    # Check additional conditions supplied
                    conditions_met = 0
                    for condition in conditions:
                        if getattr(sprite, condition) == conditions[condition]:
                            conditions_met += 1
                    if conditions_met == len(conditions):
                        return sprite
        
        # Check for specific instance
        else:
            # Basic rect check
            if self.rect.colliderect(collidee.rect):
                return collidee

    def contact_with(self, cls, side):
        """
        given class and side
        :param cls: Type
        :param side: "top", "right", "bottom", "left"
        :return: sprite or None
        """
        collidee = find_closest(self, cls)
        # Check same world
        if collidee and collidee.world == self.world:
            # Horizontal contact
            if side == "left" or side == "right":
                if (within_range(self.rect.top, collidee.rect.top, collidee.rect.bottom)
                        or within_range(self.rect.bottom, collidee.rect.top, collidee.rect.bottom)):
                    # Left contact
                    if collidee.rect.left == self.rect.right and side == "left":
                        return collidee
                    # Right contact
                    elif collidee.rect.right == self.rect.left and side == "right":
                        return collidee
            elif side == "top" or side == "bottom":
                if (within_range(self.rect.left, collidee.rect.left, collidee.rect.right)
                        or within_range(self.rect.right, collidee.rect.left, collidee.rect.right)):
                    # Top contact
                    if collidee.rect.bottom == self.rect.top and side == "top":
                        return collidee
                    # Bottom contact
                    elif collidee.rect.top == self.rect.bottom and side == "bottom":
                        return collidee
            else:
                raise ValueError(f"Invalid side {side}")

    def detect_solid(self, rect, same_world=True):
        """
        given a rect return a colliding solid Sprite or None
        :param rect: Rect
        :return: Sprite or None
        """
        for sprite in self.game.entities["ALL"]:
            if sprite.rect.colliderect(rect) and sprite.is_solid and sprite is not self:
                # If self or collidee in all world, detects
                if self.world is None or sprite.world is None:
                    return sprite
                # if same_world and same world
                elif not same_world or self.world == sprite.world:
                    return sprite
    
    def render_text(self, text, pos=(0, 0), color=BLACK):
        """
        given position relative to self, blit text
        :param text: Str
        :param pos: (int, int) *note this is relative to self
        :param color: (int, int, int) rgb
        :return: None
        """
        textsurface = self.font.render(text, True, color)
        text_rect = textsurface.get_rect()
        
        # Center Text
        centered_text_pos = pos[0]-text_rect.w/2, pos[1]-text_rect.h/2
        
        # Absolute pos from relative to self
        absolute_pos = (self.x + centered_text_pos[0], self.y + centered_text_pos[1])
        
        # Adjust for camera
        camera_adjusted_pos = self.game.camera.adjust_point(absolute_pos)
        self.game.surface.blit(textsurface, camera_adjusted_pos)
    
    def _animation_done_hook(self):
        print(f"{self} done ani")
    
    def _on_last_frame(self):
        total_frames = len(self.__class__.images[self.image_name])
        return self._frame_index % total_frames == total_frames -1
    
    def __str__(self):
        return f"{self.__class__.__name__} at {self.x, self.y}"

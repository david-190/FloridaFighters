import pygame
from math import sin 

class Entity(pygame.sprite.Sprite):
    
    def __init__(self, groups, level=None):
        super().__init__(groups)
        
        self.frame_index = 0
        self.animation_speed = 0.15
        self.direction = pygame.math.Vector2()
        self.level = level
     
    def move(self, speed):
        """Move entity with collision detection and normalization."""
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Apply horizontal movement and check collisions
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        
        # Apply vertical movement and check collisions
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        
        # Sync visual rect with hitbox position
        self.rect.center = self.hitbox.center
    
    def collision(self, direction):
        """
        Handle collision detection with spatial hash optimization.
        
        Algorithm:
        1. Check if spatial grid is available via self.level
        2. If available, query only nearby obstacles (O(1))
        3. If not available, check all obstacles (O(n)) - backwards compatible
        4. Resolve collision by adjusting hitbox position
        
        This maintains backwards compatibility while optimizing when possible.
        """
        # Determine which obstacles to check
        if hasattr(self, 'level') and self.level and hasattr(self.level, 'spatial_grid'):
            # OPTIMIZED PATH: Use spatial hash grid
            obstacles_to_check = self.level.spatial_grid.query(self.hitbox)
        else:
            # FALLBACK PATH: Check all obstacles (original behavior)
            obstacles_to_check = self.obstacle_sprites
        
        # Collision resolution
        if direction == 'horizontal':
            for sprite in obstacles_to_check:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # Moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # Moving left
                        self.hitbox.left = sprite.hitbox.right
                    
        if direction == 'vertical':
            for sprite in obstacles_to_check:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y < 0:  # Moving up
                        self.hitbox.top = sprite.hitbox.bottom
                    if self.direction.y > 0:  # Moving down
                        self.hitbox.bottom = sprite.hitbox.top
                        
    def wave_value(self):
        """Generate oscillating value for flicker effect (0 or 255)."""
        value = sin(pygame.time.get_ticks())
        
        if value >= 0:
            return 255
        else: 
            return 0
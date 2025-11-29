import pygame
from math import sin 

class Entity(pygame.sprite.Sprite):
    
    def __init__(self,groups, level=None):
        super().__init__(groups)
        
        self.frame_index = 0
        self.animation_speed = 0.15
        self.direction = pygame.math.Vector2()
        self.level = level
     
    def move(self,speed):
        """Move entity with collision detection and normalization."""
        # Normalize diagonal movement to prevent faster speed
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
    
    def collision(self,direction):
        """Handle collision detection and resolution for specified axis."""
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                    
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                        
    def wave_value(self):
        """Generate oscillating value for flicker effect (0 or 255)."""
        value = sin(pygame.time.get_ticks())
        
        if value >= 0:
            return 255
        else: 
            return 0
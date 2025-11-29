import pygame
from settings import *
from entity import Entity
from support import *
from astar import astar
import math

class Enemy(Entity):
    
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player, trigger_death_particles, add_exp, pathfinding_grid):
        super().__init__(groups)
        self.sprite_type = 'enemy'
        
        # Load and initialize animations
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        
        # Collision detection
        self.hitbox = self.rect.inflate(0,-10)
        self.obstacle_sprites = obstacle_sprites
        
        # Initialize stats from monster data
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resitance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']
        
        # Combat timers
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown_time = 400
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_exp = add_exp
        
        # Damage immunity timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300
        
        # Audio
        self.death_sound = pygame.mixer.Sound('audio/death.wav')
        self.hit_sound = pygame.mixer.Sound('audio/hit.wav')
        self.attack_sound = pygame.mixer.Sound(monster_info['attack_sound'])
        self.death_sound.set_volume(0.6)
        self.hit_sound.set_volume(0.6)
        self.attack_sound.set_volume(0.3)
                
        # Store the pathfinding grid
        self.pathfinding_grid = pathfinding_grid
        
        # Pathfinding attributes
        self.path = []
        self.path_update_cooldown = 0
    
    def import_graphics(self, name):
        """Load all animation frames for the specified monster type."""
        self.animations = {'idle': [], 'move': [], 'attack': []}
        main_path = f'graphics/monsters/{name}/'
        
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)
    
    def get_player_distance_direction(self, player):
        """Calculate distance and normalized direction vector to player."""
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()
        
        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else: 
            direction = pygame.math.Vector2()
            
        return (distance, direction)
    
    def get_grid_position(self, pos):
        """Convert pixel position to grid coordinates (row, col)."""
        col = int(pos[0] // TILESIZE)
        row = int(pos[1] // TILESIZE)
        return (row, col)
    
    def get_status(self, player):
        """Update enemy status based on distance to player."""
        distance = self.get_player_distance_direction(player)[0]
        
        if distance <= self.attack_radius and self.can_attack == True:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else: 
            self.status = 'idle'
    
    def actions(self, player):
        """Execute behavior based on current status."""
        distance = self.get_player_distance_direction(player)[0]
        
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_damage, self.attack_type)
            self.attack_sound.play()
            self.path = []
            self.direction = pygame.math.Vector2(0, 0)
            
        elif self.status == 'move':
            # Double-check distance - if out of range, stop immediately
            if distance > self.notice_radius:
                self.path = []
                self.direction = pygame.math.Vector2(0, 0)
                return
            
            # Update path periodically OR if path is empty/invalid
            self.path_update_cooldown += 1
            should_update_path = (
                self.path_update_cooldown >= 60 or
                not self.path or
                len(self.path) == 0
            )
            
            if should_update_path:
                self.path_update_cooldown = 0
                
                # Get grid positions
                start = self.get_grid_position(self.rect.center)
                goal = self.get_grid_position(player.rect.center)
                
                # Validate grid positions
                grid = self.pathfinding_grid
                if (0 <= start[1] < len(grid[0]) and
                    0 <= start[0] < len(grid) and
                    0 <= goal[1] < len(grid[0]) and
                    0 <= goal[0] < len(grid)):
                    
                    # Compute path - astar expects (x, y) format
                    start_astar = (start[1], start[0])
                    goal_astar = (goal[1], goal[0])
                    self.path = astar(grid, start_astar, goal_astar)
                    
                    # Validate path
                    if self.path:
                        valid_path = True
                        for step in self.path:
                            col, row = step
                            if not (0 <= col < len(grid[0]) and 0 <= row < len(grid)) or not grid[row][col]:
                                valid_path = False
                                break
                        if not valid_path:
                            self.path = []
            
            # Follow the path
            if self.path and len(self.path) > 0:
                next_step = self.path[0]
                next_pixel = (next_step[0] * TILESIZE + TILESIZE // 2, 
                            next_step[1] * TILESIZE + TILESIZE // 2)
                direction = pygame.math.Vector2(next_pixel) - pygame.math.Vector2(self.rect.center)
                
                if direction.magnitude() < 10:
                    self.path.pop(0)
                    if len(self.path) == 0:
                        self.direction = self.get_player_distance_direction(player)[1]
                else:
                    if direction.magnitude() > 0:
                        self.direction = direction.normalize()
            else:
                # Fallback to direct movement
                self.direction = self.get_player_distance_direction(player)[1]
        
        else:  # idle
            self.path = []
            self.direction = pygame.math.Vector2(0, 0)
    
    def animate(self):
        """Update animation frame and apply visual effects."""
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed

        if self.frame_index >= len(self.animations[self.status]):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0
            
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)
        
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)
        
    def cooldown(self):
        """Manage attack and invulnerability cooldown timers."""
        current_time = pygame.time.get_ticks()
        
        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown_time:
                self.can_attack = True
        
        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True
            
    def get_damge(self, player, attack_type):
        """Apply damage to enemy if not currently invulnerable."""
        if self.vulnerable:  
            self.hit_sound.play()
            self.direction = self.get_player_distance_direction(player)[1]
            
            if attack_type == 'weapon':
                self.health -= player.get_full_weapon_damage()
            else:
                self.health -= player.get_full_magic_damage()
            
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False
        
    def check_death(self):
        """Remove enemy and trigger effects if health depleted."""
        if self.health <= 0:
            self.kill()
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.add_exp(self.exp)
            self.death_sound.play()
    
    def hit_reaction(self):
        """Apply knockback when enemy is hit."""
        if not self.vulnerable:
            self.direction *= -self.resitance
    
    def move(self, speed):
        """Move entity with collision detection and normalization."""
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        predicted_hitbox = self.hitbox.copy()
        predicted_hitbox.x += self.direction.x * speed
        predicted_hitbox.y += self.direction.y * speed
        
        collision = False
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(predicted_hitbox):
                collision = True
                break
        
        if not collision:
            self.hitbox.x += self.direction.x * speed
            self.collision('horizontal')
            self.hitbox.y += self.direction.y * speed
            self.collision('vertical')
            self.rect.center = self.hitbox.center
        else:
            adjusted = False
            for angle in [30, -30, 60, -60]:
                rad_angle = math.radians(angle)
                new_direction = pygame.math.Vector2(
                    self.direction.x * math.cos(rad_angle) - self.direction.y * math.sin(rad_angle),
                    self.direction.x * math.sin(rad_angle) + self.direction.y * math.cos(rad_angle)
                )
                
                adjusted_hitbox = self.hitbox.copy()
                adjusted_hitbox.x += new_direction.x * speed
                adjusted_hitbox.y += new_direction.y * speed
                
                collision = False
                for sprite in self.obstacle_sprites:
                    if sprite.hitbox.colliderect(adjusted_hitbox):
                        collision = True
                        break
                
                if not collision:
                    self.direction = new_direction
                    self.hitbox.x += self.direction.x * speed
                    self.hitbox.y += self.direction.y * speed
                    self.rect.center = self.hitbox.center
                    adjusted = True
                    break
            
            if not adjusted:
                self.hitbox.x += self.direction.x * speed
                self.collision('horizontal')
                self.hitbox.y += self.direction.y * speed
                self.collision('vertical')
                self.rect.center = self.hitbox.center
    
    def update(self):
        """Update enemy state each frame."""
        self.hit_reaction()
        self.move(self.speed)
        self.cooldown()
        self.animate()
        self.check_death()
    
    def enemy_update(self, player):
        """Update AI behavior based on player position."""
        self.get_status(player = player)
        self.actions(player)
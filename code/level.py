import pygame
from settings import TILESIZE, DEBUG_MODE
from tile import Tile
from player import Player
from support import import_csv_layout, import_folder
from random import choice, randint
from weapon import Weapon
from ui import UI
from death_screen import DeathScreen
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade

class Level():
    
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False 
        
        # Sprite groups for rendering and collision detection
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()       
        
        # Combat-related sprite groups
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        
        
        self.create_map()

        self.ui = UI()
        self.upgrade = Upgrade(self.player)

        self.death_screen = DeathScreen(self.display_surface)
        self.is_dead = False

        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)
        
        # Pathfinding grid (added)
        self.pathfinding_grid = None
    
    def create_map(self):
        """Load CSV layouts and graphics, then instantiate all map tiles and entities."""
        layouts = {
            'boundary': import_csv_layout('map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('map/map_Grass.csv'),
            'object': import_csv_layout('map/map_Objects.csv'),
            'entities': import_csv_layout('map/map_Entities.csv')
        }
        graphics = {
            'grass': import_folder('graphics/Grass'),
            'object': import_folder('graphics/Objects')
        }
        
        # Create pathfinding grid (added)
        grid_width = len(layouts['boundary'][0])
        grid_height = len(layouts['boundary'])
        self.pathfinding_grid = [[True] * grid_width for _ in range(grid_height)]
        
        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        # Convert grid coordinates to pixel positions
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE

                        if style == 'boundary':
                            tile = Tile(pos = (x, y), groups = [self.obstacle_sprites], sprite_type = 'invisible')
                        
                        if style == 'grass':
                            random_grass_image = choice(graphics['grass'])
                            tile = Tile(pos = (x, y), groups = [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], sprite_type = 'grass', surface = random_grass_image)
                        
                        if style == 'object':
                            # Use column value as index to select correct graphic
                            surf = graphics['object'][int(col)]
                            tile = Tile(pos = (x, y), groups = [self.visible_sprites, self.obstacle_sprites], sprite_type = 'object', surface = surf)
                        
                        if style == 'entities':
                            if col == '394':
                                self.player = Player(pos = (x, y), 
                                                groups = [self.visible_sprites],           
                                                obstacle_sprites = self.obstacle_sprites,
                                                create_attack = self.create_attack,
                                                destroy_attack = self.destroy_attack,
                                                create_magic = self.create_magic)
                                self.player.level = self  # Set level reference
                            else:
                                # Map entity IDs to monster types
                                if col == '390':
                                    monster_name = 'bamboo'
                                elif col == '391':
                                    monster_name = 'spirit'
                                elif col == '392':
                                    monster_name = 'raccoon'
                                else:
                                    monster_name = 'squid'
                                
                                enemy = Enemy(monster_name = monster_name, 
                                        pos = (x,y), 
                                        groups = [self.visible_sprites, self.attackable_sprites],
                                        obstacle_sprites = self.obstacle_sprites,
                                        damage_player = self.damage_player,
                                        trigger_death_particles = self.trigger_death_particles,
                                        add_exp = self.add_exp,
                                        pathfinding_grid = self.pathfinding_grid)
                                enemy.level = self  # Set level reference
                        # Mark obstacles in pathfinding grid (added)
                        if style in ['boundary', 'object']:
                            # Ensure grid indices are within bounds
                            if 0 <= row_index < len(self.pathfinding_grid) and 0 <= col_index < len(self.pathfinding_grid[0]):
                                self.pathfinding_grid[len(self.pathfinding_grid) - row_index - 1][col_index] = False
        
    def create_attack(self):
        """Instantiate player's weapon sprite."""
        self.current_attack = Weapon(self.player, 
                                     groups = [self.visible_sprites, self.attack_sprites])
    
    def create_magic(self, style, strength, cost):
        """Execute magic attack based on style type."""
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])
            
        if style == 'flame':
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])
    
    def destroy_attack(self):
        """Remove current attack sprite from all groups."""
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None
    
    def destroy_grass(self):
        """Remove grass when attacked and drop items."""
        for attack_sprite in self.attack_sprites:
            # Find overlapping grass sprites
            collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
            for sprite in collision_sprites:
                if sprite.sprite_type == 'grass':
                    # Get grid position
                    x = sprite.rect.centerx // TILESIZE
                    y = sprite.rect.centery // TILESIZE
                    
                    # Update pathfinding grid
                    if 0 <= y < len(self.pathfinding_grid) and 0 <= x < len(self.pathfinding_grid[0]):
                        self.pathfinding_grid[y][x] = True
                    
                    # Create particles and items
                    pos = sprite.rect.center
                    self.animation_player.create_grass_particles(pos)
                    sprite.kill()
    
    
    def player_attack_logic(self):
        """Check for collisions between attack sprites and attackable entities."""
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprite = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)

                if collision_sprite:
                    for target_sprite in collision_sprite:
                        if target_sprite.sprite_type == 'grass':
                            # Spawn particle effects and destroy grass
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0,75)
                    
                            for leaf in range(randint(3,6)):
                                self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
                            
                            target_sprite.kill()
                        else: 
                            target_sprite.get_damge(self.player, attack_sprite.sprite_type)
    
    def damage_player(self, amount, attack_type):
        """Apply damage to player if not currently invulnerable."""
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])
            
    def trigger_death_particles(self, pos, particle_type): 
        """Spawn particle effect at specified position."""
        self.animation_player.create_particles(particle_type, pos, [self.visible_sprites])
        
    def add_exp(self, amount):
        """Add experience points to player."""
        self.player.exp += amount
        
    def toggle_menu(self):
        """Toggle pause state for upgrade menu."""
        self.game_paused = not self.game_paused
        
    def run(self):
        """Main level update and render loop."""
        # Check for player death
        if self.player.health <= 0:
            self.is_dead = True

        if self.is_dead:
            self.death_screen.draw()
            return

        # Render sprites and UI
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)
               
        if self.game_paused:
            self.upgrade.display() 
        else:
            # Update game state only when not paused
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()

        
class YSortCameraGroup(pygame.sprite.Group):
    """Custom sprite group with camera offset and Y-axis sorting for depth."""
    
    def __init__(self):
       super().__init__()
       
       self.display_surface = pygame.display.get_surface()
       # Calculate screen center for camera positioning
       self.half_width = self.display_surface.get_size()[0] // 2
       self.half_height = self.display_surface.get_size()[1] // 2
       # Offset vector keeps player centered on screen
       self.offset = pygame.math.Vector2()
       
       self.floor_surface = pygame.image.load('graphics/tilemap/ground.png').convert()
       self.floor_rect = self.floor_surface.get_rect(topleft = (0,0))
       
    def custom_draw(self, player):
        """Render all sprites with camera offset centered on player."""
        # Calculate offset to keep player centered
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height
       
        # Draw floor with offset
        offset_floor = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surface, offset_floor)
        
        # Draw sprites sorted by Y position for depth illusion
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
            
    def enemy_update(self,player):
        """Update all enemy sprites with player position."""
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
        
        for enemy in enemy_sprites:
            enemy.enemy_update(player)
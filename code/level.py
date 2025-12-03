import sys
import pygame
from settings import TILESIZE, DEBUG_MODE
from tile import Tile
from player import Player
from support import import_csv_layout, import_folder
from random import choice, randint
from weapon import Weapon
from ui import UI
from death_screen import DeathScreen
from game_complete_screen import GameCompleteScreen
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade
from spatial_hash import SpatialHashGrid


class Level():
    
    def __init__(self, input_manager=None, game=None):
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False 
        self.input_manager = input_manager
        self.game = game  # Store reference to Game instance
        
        # Sprite groups for rendering and collision detection
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()       
        
        # Combat-related sprite groups
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        
        # Spatial Hash Grid for optimized collision detection
        self.spatial_grid = SpatialHashGrid(cell_size=TILESIZE * 3)
        
        self.create_map()

        self.ui = UI(self.input_manager)
        # Pass the game instance to the Upgrade menu
        self.upgrade = Upgrade(self.player, self.input_manager, game=self.game)

        self.death_screen = DeathScreen(self.display_surface)
        self.is_dead = False
        self.game_complete_screen = GameCompleteScreen(self.display_surface)
        self.game_complete = False

        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)
        
        # Pathfinding grid
        self.pathfinding_grid = None
        
    def get_state(self):
        # Return a dictionary representing the current level state.
        return {
            'player_state': self.player.get_state(),
            'game_time': pygame.time.get_ticks() // 1000,  # Convert to seconds
            'game_complete': self.game_complete,
            'game_paused': self.game_paused
        }

    def load_state(self, state):
        # Load level state from a dictionary.
        if not state:
            return
            
        if 'player_state' in state:
            self.player.load_state(state['player_state'])
            
        if 'game_complete' in state:
            self.game_complete = state['game_complete']
            
        if 'game_paused' in state:
            self.game_paused = state['game_paused']
            
        # Reset any necessary game state
        self.is_dead = False
    
    def create_map(self):
        # Load CSV layouts and graphics, then instantiate all map tiles and entities.
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
        
        # Create pathfinding grid
        grid_width = len(layouts['boundary'][0])
        grid_height = len(layouts['boundary'])
        self.pathfinding_grid = [[True] * grid_width for _ in range(grid_height)]
        
        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE

                        if style == 'boundary':
                            tile = Tile(pos = (x, y), groups = [self.obstacle_sprites], sprite_type = 'invisible')
                        
                        if style == 'grass':
                            random_grass_image = choice(graphics['grass'])
                            tile = Tile(pos = (x, y), groups = [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], sprite_type = 'grass', surface = random_grass_image)
                        
                        if style == 'object':
                            surf = graphics['object'][int(col)]
                            tile = Tile(pos = (x, y), groups = [self.visible_sprites, self.obstacle_sprites], sprite_type = 'object', surface = surf)
                        
                        if style == 'entities':
                            if col == '394':
                                self.player = Player(
                                    pos = (x, y),
                                    groups = [self.visible_sprites],
                                    obstacle_sprites = self.obstacle_sprites,
                                    create_attack = self.create_attack,
                                    destroy_attack = self.destroy_attack,
                                    create_magic = self.create_magic,
                                    input_manager = self.input_manager
                                )
                                self.player.level = self  # Set level reference
                            else:
                                # Map entity IDs to monster types
                                if col == '390':
                                    monster_name = 'owl'
                                elif col == '391':
                                    monster_name = 'squirrel'
                                elif col == '392':
                                    monster_name = 'raccoon'
                                else:
                                    monster_name = 'eye'
                                
                                enemy = Enemy(monster_name = monster_name, 
                                        pos = (x,y), 
                                        groups = [self.visible_sprites, self.attackable_sprites],
                                        obstacle_sprites = self.obstacle_sprites,
                                        damage_player = self.damage_player,
                                        trigger_death_particles = self.trigger_death_particles,
                                        add_exp = self.add_exp,
                                        pathfinding_grid = self.pathfinding_grid)
                                enemy.level = self  # Set level reference
                        
                        # Mark obstacles in pathfinding grid
                        if style in ['boundary', 'object', 'grass']:
                            if 0 <= row_index < len(self.pathfinding_grid) and 0 <= col_index < len(self.pathfinding_grid[0]):
                                self.pathfinding_grid[row_index][col_index] = False
        
    def create_attack(self):
        # Instantiate player's weapon sprite.
        self.current_attack = Weapon(self.player, 
                                     groups = [self.visible_sprites, self.attack_sprites])
    
    def create_magic(self, style, strength, cost):
        # Execute magic attack based on style type.
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])
            
        if style == 'flame':
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])
    
    def destroy_attack(self):
        # Remove current attack sprite from all groups.
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None
    
    def destroy_grass(self):
        # Remove grass when attacked and drop items.
        for attack_sprite in self.attack_sprites:
            collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
            for sprite in collision_sprites:
                if sprite.sprite_type == 'grass':
                    x = sprite.rect.centerx // TILESIZE
                    y = sprite.rect.centery // TILESIZE
                    
                    if 0 <= y < len(self.pathfinding_grid) and 0 <= x < len(self.pathfinding_grid[0]):
                        self.pathfinding_grid[y][x] = True
                    
                    pos = sprite.rect.center
                    self.animation_player.create_grass_particles(pos)
                    sprite.kill()
    
    def player_attack_logic(self):
        # Check for collisions between attack sprites and attackable entities.
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprite = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)

                if collision_sprite:
                    for target_sprite in collision_sprite:
                        if target_sprite.sprite_type == 'grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0,75)
                    
                            for leaf in range(randint(3,6)):
                                self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
                            
                            target_sprite.kill()
                        else: 
                            target_sprite.get_damge(self.player, attack_sprite.sprite_type)
    
    def damage_player(self, amount, attack_type, source_pos=None):
        # Apply damage to player if not currently invulnerable.
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])
            if source_pos is not None:
                self.player.apply_knockback(source_pos)
            
    def trigger_death_particles(self, pos, particle_type): 
        # Spawn particle effect at specified position.
        self.animation_player.create_particles(particle_type, pos, [self.visible_sprites])
        
    def add_exp(self, amount):
        # Add experience points to player.
        self.player.exp += amount
        
    def toggle_menu(self):
        # Toggle pause state for upgrade menu.
        self.game_paused = not self.game_paused
        if self.game_paused and self.input_manager:
            # Require the player to press the quit input while in the menu
            self.input_manager.consume_quit_request()
    
    def _rebuild_spatial_grid(self):
        """
        Rebuild the spatial hash grid each frame.
        
        Algorithm:
        1. Clear the grid (O(1) - just clears dictionary)
        2. Insert all obstacle sprites (O(n) where n = number of obstacles)
        3. Grid is now ready for O(1) queries
        
        This happens every frame because sprites can move.
        Cost is amortized across all collision queries in the frame.
        """
        self.spatial_grid.clear()
        
        # Insert all obstacles into spatial grid
        for sprite in self.obstacle_sprites:
            self.spatial_grid.insert(sprite)
        
    def _draw_enemy_paths_debug(self):
        """Render enemy A* paths when debug mode is enabled."""
        offset = self.visible_sprites.offset
        for sprite in self.visible_sprites:
            if getattr(sprite, 'sprite_type', None) != 'enemy':
                continue

            path = getattr(sprite, 'path', None)
            if not path:
                continue

            points = []
            for col, row in path:
                px = col * TILESIZE + TILESIZE // 2
                py = row * TILESIZE + TILESIZE // 2
                screen_pos = pygame.math.Vector2(px, py) - offset
                points.append((int(screen_pos.x), int(screen_pos.y)))

            if not points:
                continue

            if len(points) > 1:
                pygame.draw.lines(self.display_surface, (255, 215, 0), False, points, 2)

            for point in points:
                pygame.draw.circle(self.display_surface, (255, 140, 0), point, 4)

    def run(self):
        # Main level update and render loop.
        # Check for player death
        if self.player.health <= 0:
            self.is_dead = True

        if self.is_dead:
            self.death_screen.draw()
            return

        if not self.game_complete:
            self._check_game_completion()

        if self.game_complete:
            self.game_complete_screen.draw()
            if self.input_manager and self.input_manager.consume_quit_request():
                pygame.quit()
                sys.exit()
            return

        # Rebuild spatial grid each frame
        self._rebuild_spatial_grid()

        # Render sprites and UI
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)
        
        # Debug: Visualize spatial grid (only if DEBUG_MODE is True)
        if DEBUG_MODE:
            self.spatial_grid.visualize_debug(self.display_surface, self.visible_sprites.offset)

            # Show stats
            stats = self.spatial_grid.get_stats()
            from debug import debug
            debug(f"Spatial Grid - Sprites: {stats['total_sprites']}, Cells: {stats['total_cells']}", y=40)
            debug(f"Max/Cell: {stats['max_sprites_per_cell']}, Queries: {stats['queries_this_frame']}", y=70)
            self._draw_enemy_paths_debug()
               
        if self.game_paused:
            self.upgrade.display()
            if self.upgrade.consume_quit_request():
                pygame.quit()
                sys.exit()
        else:
            # Update game state only when not paused
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()
            self._check_game_completion()

    def _check_game_completion(self):
        if self.game_complete:
            return

        for sprite in self.visible_sprites:
            if getattr(sprite, 'sprite_type', None) == 'enemy':
                return

        self.game_complete = True

        
class YSortCameraGroup(pygame.sprite.Group):
    # Custom sprite group with camera offset and Y-axis sorting for depth.
    
    def __init__(self):
       super().__init__()
       
       self.display_surface = pygame.display.get_surface()
       self.half_width = self.display_surface.get_size()[0] // 2
       self.half_height = self.display_surface.get_size()[1] // 2
       self.offset = pygame.math.Vector2()
       
       self.floor_surface = pygame.image.load('graphics/tilemap/ground.png').convert()
       self.floor_rect = self.floor_surface.get_rect(topleft = (0,0))
       
    def custom_draw(self, player):
        # Render all sprites with camera offset centered on player.
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height
       
        offset_floor = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surface, offset_floor)
        
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
            
    def enemy_update(self,player):
        # Update all enemy sprites with player position.
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
        
        for enemy in enemy_sprites:
            enemy.enemy_update(player)
import pygame
from settings import *
from support import *
from entity import *

class Player(Entity):
    
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic, input_manager=None):
        super().__init__(groups)
        
        self.image = pygame.image.load('graphics/player/down_idle/idle_down.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-6 , HITBOX_OFFSET['player'])
        
        self.import_player_assets()
        self.status = 'down'
        
        # Attack state
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None
        
        self.obstacle_sprites = obstacle_sprites

        # Weapon system
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200
        
        # Magic system
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None
        
        # Player attributes
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 6}
        self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic': 10, 'speed': 10}
        self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic': 100, 'speed': 100}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 0
        self.speed = self.stats['speed']
        
        # Damage immunity
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500
        
        self.weapon_attack_sound = pygame.mixer.Sound('audio/sword.wav')
        self.weapon_attack_sound.set_volume(0.4)
        
        # Unified input provider
        self.input_manager = input_manager
        
        # Knockback physics state
        self.knockback_velocity = pygame.math.Vector2()
        self.knockback_decay = 0.85

    def get_state(self):
        # Return a dictionary representing the player's current state.
        return {
            'position': (self.rect.x, self.rect.y),
            'health': self.health,
            'energy': self.energy,
            'exp': self.exp,
            'weapon_index': self.weapon_index,
            'magic_index': self.magic_index,
            'stats': self.stats.copy(),
            'max_stats': self.max_stats.copy(),
            'upgrade_cost': self.upgrade_cost.copy()
        }

    def get_stat_name_by_index(self, index):
        # Get the name of a stat by its index.
        if 0 <= index < len(self.stats):
            return list(self.stats.keys())[index]
        return None

    def load_state(self, state):
        # Load player state from a dictionary.
        if not state:
            return
            
        self.rect.x, self.rect.y = state.get('position', (self.rect.x, self.rect.y))
        self.hitbox.center = self.rect.center
        self.health = state.get('health', self.health)
        self.energy = state.get('energy', self.energy)
        self.exp = state.get('exp', self.exp)
        
        # Only update weapon/magic if they exist in the save
        if 'weapon_index' in state:
            self.weapon_index = state['weapon_index']
            self.weapon = list(weapon_data.keys())[self.weapon_index]
            
        if 'magic_index' in state:
            self.magic_index = state['magic_index']
            self.magic = list(magic_data.keys())[self.magic_index]
            
        # Update stats if they exist in the save
        if 'stats' in state:
            self.stats = state['stats'].copy()
            self.speed = self.stats['speed']
            
        if 'max_stats' in state:
            self.max_stats = state['max_stats'].copy()
            
        if 'upgrade_cost' in state:
            self.upgrade_cost = state['upgrade_cost'].copy()

    def import_player_assets(self):
        # Load all player animation frames.
        character_path = 'graphics/player/'
        self.animations = {'up': [],'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': [],}
        
        for animation in self.animations.keys():
            full_path = character_path + '/' + animation
            self.animations[animation] = import_folder(full_path)
        
    def input(self):
        # Handle player input from keyboard or InputManager.
        if self.input_manager:
            self._input_from_manager()
        else:
            self._input_from_keyboard()
        
    def get_status(self):
        # Update player status string based on movement and action state.
        # Apply idle status when stationary
        if self.direction.x == 0 and self.direction.y == 0:
            if 'idle' not in self.status and 'attack' not in self.status:
                self.status = self.status + '_idle'
        
        if self.attacking:
            # Prevent movement during attack
            self.direction.x = 0
            self.direction.y = 0
            
            if 'attack' not in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle', '_attack')
                else: 
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')
    
    def cooldowns(self):
        # Manage cooldown timers for attacks, switching, and invulnerability.
        current_time = pygame.time.get_ticks()
        
        if self.attacking:
            weapon_cooldown = weapon_data[self.weapon]['cooldown']
            if current_time - self.attack_time >= self.attack_cooldown + weapon_cooldown:
                self.attacking = False
                self.destroy_attack()

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True
        
        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
                self.can_switch_magic = True
        
        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True
   
    def animate(self):
        # Update animation frame and apply visual effects.
        animation = self.animations[self.status]
        
        self.frame_index += self.animation_speed
        
        if self.frame_index >= len(animation):
            self.frame_index  = 0
            
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)
        
        # Flicker effect during invulnerability
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)
        
    def get_full_weapon_damage(self):
        # Calculate total weapon damage including base attack stat.
        base_damage = self.stats['attack']
        weapon_damage = weapon_data[self.weapon]['damage']
        
        return base_damage + weapon_damage
    
    def get_full_magic_damage(self):
        # Calculate total magic damage including base magic stat.
        base_damage = self.stats['magic']
        spell_damage = magic_data[self.magic]['strength']
        
        return base_damage + spell_damage
        
    def get_value_by_index(self, index):
        # Retrieve stat value by index for upgrade menu.
        return list(self.stats.values())[index]
    
    def get_cost_by_index(self, index):
        # Retrieve upgrade cost by index for upgrade menu.
        return list(self.upgrade_cost.values())[index]
        
    def upgrade_stat(self, stat_name):
        # Upgrade the specified stat and increase its upgrade cost.
        if stat_name in self.stats and stat_name in self.max_stats:
            # Increase the stat by 1, but don't exceed max
            if self.stats[stat_name] < self.max_stats[stat_name]:
                self.stats[stat_name] += 1
                
                # Special handling for speed to update movement
                if stat_name == 'speed':
                    self.speed = self.stats['speed']
                    
                # Increase the cost for the next upgrade
                self.upgrade_cost[stat_name] = int(self.upgrade_cost[stat_name] * 1.5)
                return True
        return False
    
    def energy_recovery(self):
        # Gradually restore energy based on magic stat.
        if self.energy <= self.stats['energy']:
            self.energy += 0.01 * self.stats['magic']
        else:
            self.energy = self.stats['energy']

    def _input_from_keyboard(self):
        if self.attacking:
            return

        keys_pressed = pygame.key.get_pressed()

        # Movement input
        if keys_pressed[pygame.K_w]:
            self.direction.y = -1
            self.status = 'up'
        elif keys_pressed[pygame.K_s]:
            self.direction.y = +1
            self.status = 'down'
        else:
            self.direction.y = 0 

        if keys_pressed[pygame.K_a]:
            self.direction.x = -1
            self.status = 'left'  
        elif keys_pressed[pygame.K_d]:
            self.direction.x = +1
            self.status = 'right'
        else: 
            self.direction.x = 0

        # Weapon attack
        if keys_pressed[pygame.K_h]:
            self._start_weapon_attack()

        # Magic attack
        if keys_pressed[pygame.K_j]:
            self._start_magic_attack()

        # Weapon switching
        if keys_pressed[pygame.K_k] and self.can_switch_weapon:
            self._cycle_weapon()

        # Magic switching
        if keys_pressed[pygame.K_l] and self.can_switch_magic:
            self._cycle_magic()

    def _input_from_manager(self):
        move = self.input_manager.get_move_vector()
        if not self.attacking:
            self.direction.xy = move.xy
            self._update_status_from_vector(move)
        else:
            self.direction.update(0, 0)

        if not self.attacking and self.input_manager.attack_active:
            self._start_weapon_attack()

        if not self.attacking and self.input_manager.magic_active:
            self._start_magic_attack()

        if self.input_manager.consume_weapon_switch() and self.can_switch_weapon:
            self._cycle_weapon()

        if self.input_manager.consume_magic_switch() and self.can_switch_magic:
            self._cycle_magic()

    def _start_weapon_attack(self):
        self.attacking = True 
        self.attack_time = pygame.time.get_ticks()
        self.create_attack()
        self.weapon_attack_sound.play()

    def _start_magic_attack(self):
        self.attacking = True 
        self.attack_time = pygame.time.get_ticks()
        style = list(magic_data.keys())[self.magic_index]
        strength = list(magic_data.values())[self.magic_index]["strength"]
        cost = list(magic_data.values())[self.magic_index]["cost"]
        self.create_magic(style, strength, cost)

    def _cycle_weapon(self):
        self.can_switch_weapon = False
        self.weapon_switch_time = pygame.time.get_ticks()
        if self.weapon_index < len(list(weapon_data.keys())) - 1:
            self.weapon_index += 1
        else: 
            self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]

    def _cycle_magic(self):
        self.can_switch_magic = False 
        self.magic_switch_time = pygame.time.get_ticks()
        if self.magic_index < len(list(magic_data.keys())) - 1:
            self.magic_index += 1
        else: 
            self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]

    def _update_status_from_vector(self, vector):
        if vector.x == 0 and vector.y == 0:
            return
        if abs(vector.x) > abs(vector.y):
            self.status = 'right' if vector.x > 0 else 'left'
        else:
            self.status = 'down' if vector.y > 0 else 'up'
    
    def apply_knockback(self, source_position, strength=12):
        # Receive an impulse pushing the player away from the source position.
        direction = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(source_position)
        if direction.length() == 0:
            return
        self.knockback_velocity = direction.normalize() * strength
    
    def _apply_knockback_motion(self):
        """Integrate current knockback velocity with collision resolution."""
        if self.knockback_velocity.length_squared() <= 0.05:
            self.knockback_velocity.update(0, 0)
            return False

        displacement = self.knockback_velocity
        original_direction = self.direction.copy()
        temp_direction = pygame.math.Vector2(
            1 if displacement.x > 0 else -1 if displacement.x < 0 else 0,
            1 if displacement.y > 0 else -1 if displacement.y < 0 else 0
        )

        if displacement.x != 0:
            self.hitbox.x += displacement.x
            self.direction.x = temp_direction.x
            self.collision('horizontal')

        if displacement.y != 0:
            self.hitbox.y += displacement.y
            self.direction.y = temp_direction.y
            self.collision('vertical')

        self.rect.center = self.hitbox.center
        self.direction = original_direction

        self.knockback_velocity *= self.knockback_decay
        if self.knockback_velocity.length_squared() <= 0.05:
            self.knockback_velocity.update(0, 0)

        return True
    
    def update(self):
        """Update player state each frame."""
        knockback_active = self._apply_knockback_motion()
        if not knockback_active:
            self.input()
        else:
            self.direction.update(0, 0)
        self.cooldowns()
        self.get_status()
        self.animate()
        if not knockback_active:
            self.move(self.stats['speed'])
        self.energy_recovery()
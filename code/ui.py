import pygame
from settings import *

class UI:
    
    def __init__(self, input_manager=None):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.input_manager = input_manager
        
        # Health and energy bar positions
        self.health_bar_rect = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        self.energy_bar_rect = pygame.Rect(10, 34, ENERGY_BAR_WIDTH, BAR_HEIGHT)
        
        # Load weapon graphics
        self.weapon_graphics = []
        for weapon in weapon_data.values(): 
            path = weapon['graphic']
            weapon = pygame.image.load(path).convert_alpha()
            self.weapon_graphics.append(weapon)

        # Load magic graphics
        self.magic_graphics = []
        for magic in magic_data.values(): 
            path = magic['graphic']
            print(path)
            magic = pygame.image.load(path).convert_alpha()
            self.magic_graphics.append(magic)
    
    def show_bar(self, current, max_amount, bg_rect, color):
        """Draw stat bar with background and border."""
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        
        # Calculate bar width based on current stat percentage
        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width
        
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect, 3)
        
    def show_exp(self, exp):
        """Display experience points in bottom-right corner."""
        text_surf = self.font.render(str(int(exp)), False, TEXT_COLOR)
        x = self.display_surface.get_size()[0] - 20
        y = self.display_surface.get_size()[1] - 20
        text_rect = text_surf.get_rect(bottomright = (x, y))
    
        box_rect = text_rect.inflate(20, 20)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, box_rect)
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, box_rect, 3)
        return box_rect
    
    def selection_box(self, left, top, has_switched):
        """Draw selection box with highlight border if recently switched."""
        bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR , bg_rect)
        
        if has_switched: 
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE , bg_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR , bg_rect, 3) 
            
        return bg_rect
    
    def weapon_overlay(self, weapon_index, has_switched, scheme):
        """Display current weapon in selection box."""
        bg_rect = self.selection_box(10, 630, has_switched)
        weapon_surf = self.weapon_graphics[weapon_index]
        weapon_rect  = weapon_surf.get_rect(center = bg_rect.center )
        self.display_surface.blit(weapon_surf, weapon_rect)
        label = self._weapon_label_for_scheme(scheme)
        self._draw_box_label(bg_rect, label)
        return bg_rect
    
    def magic_overlay(self, magic_index, has_switched, scheme):
        """Display current magic ability in selection box."""
        bg_rect_magic = self.selection_box(80, 635, has_switched)
        magic_surf = self.magic_graphics[magic_index]
        magic_rect = magic_surf.get_rect(center = bg_rect_magic.center)
        self.display_surface.blit(magic_surf, magic_rect)
        label = self._magic_label_for_scheme(scheme)
        self._draw_box_label(bg_rect_magic, label)
        return bg_rect_magic
        
    def _draw_box_label(self, box_rect, text):
        label_surf = self.font.render(text, True, TEXT_COLOR)
        label_rect = label_surf.get_rect(midtop=(box_rect.centerx, box_rect.bottom + 4))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, label_rect.inflate(8, 4))
        self.display_surface.blit(label_surf, label_rect)

    def _weapon_label_for_scheme(self, scheme):
        if scheme == 'gamepad':
            return 'X'
        if scheme == 'touch':
            return 'Tap'
        return 'H'

    def _magic_label_for_scheme(self, scheme):
        if scheme == 'gamepad':
            return 'Y'
        if scheme == 'touch':
            return 'Tap'
        return 'J'

    def _draw_exp_label(self, box_rect, scheme):
        if scheme == 'gamepad':
            text = 'Back'
        elif scheme == 'touch':
            text = 'Tap center'
        else:
            text = 'ESC'
        label_surf = self.font.render(text, True, TEXT_COLOR)
        label_rect = label_surf.get_rect(midbottom=(box_rect.centerx, box_rect.top - 6))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, label_rect.inflate(8, 4))
        self.display_surface.blit(label_surf, label_rect)

    def display(self, player):
        """Render all UI elements with current player stats."""
        self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR)
        self.show_bar(player.energy, player.stats['energy'], self.energy_bar_rect, ENERGY_COLOR)
        
        scheme = self.input_manager.get_primary_scheme() if self.input_manager else None
        exp_rect = self.show_exp(player.exp)
        
        self.weapon_overlay(player.weapon_index, not player.can_switch_weapon, scheme)
        self.magic_overlay(player.magic_index, not player.can_switch_magic, scheme)
        self._draw_exp_label(exp_rect, scheme)
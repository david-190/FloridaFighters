import pygame
from settings import *

class Upgrade:
    
    def __init__(self, player, input_manager=None, game=None):
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.input_manager = input_manager
        self.game = game  # Reference to the Game class for save/load
        
        # Use only the player stats for the upgrade menu
        self.attribute_names = list(player.stats.keys())
        self.attribute_nr = len(self.attribute_names)
        self.max_values = list(player.max_stats.values())
        
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        
        # Calculate item dimensions
        self.height = self.display_surface.get_size()[1] * 0.8
        self.width = self.display_surface.get_size()[0] // (self.attribute_nr + 1)
        self.create_items()
        
        # Navigation state
        self.selection_index = 0
        self.selection_time = None
        self.can_move = True
        self.quit_requested = False
        self.notification_text = ""
        self.notification_time = 0
        
    def input(self):
        # Handle upgrade menu navigation, selection, and save/load keybinds.
        keys = pygame.key.get_pressed()
        nav_input = 0
        confirm_pressed = keys[pygame.K_SPACE]
        quit_input = keys[pygame.K_q]
        
        # Check for save/load keybinds
        if keys[pygame.K_s] and pygame.key.get_mods() & pygame.KMOD_CTRL:
            if self.game and self.game.save_game():
                self.notification_text = "Game Saved"
                self.notification_time = pygame.time.get_ticks() + 2000
        elif keys[pygame.K_l] and pygame.key.get_mods() & pygame.KMOD_CTRL:
            if self.game and self.game.load_game():
                self.notification_text = "Game Loaded"
                self.notification_time = pygame.time.get_ticks() + 2000

        if keys[pygame.K_RIGHT]:
            nav_input = 1
        elif keys[pygame.K_LEFT]:
            nav_input = -1

        if self.input_manager:
            nav_from_manager = self.input_manager.consume_menu_nav()
            if nav_input == 0:
                nav_input = nav_from_manager
            confirm_pressed = confirm_pressed or self.input_manager.consume_confirm_action()
            quit_input = quit_input or self.input_manager.consume_quit_request()

        if self.can_move:
            if nav_input == 1 and self.selection_index < self.attribute_nr - 1:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            elif nav_input == -1 and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            if confirm_pressed and self.selection_index < len(self.item_list):
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.item_list[self.selection_index].trigger(self.player)

        if quit_input:
            self.quit_requested = True
        
    def selection_cooldown(self):
        # Manage input cooldown to prevent rapid selection changes.
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            
            if current_time - self.selection_time >= 300:
                self.can_move = True
                
    def create_items(self):
        # Generate upgrade items with calculated positions.
        self.item_list = []
        
        for index, item in enumerate(range(self.attribute_nr)):
            # Calculate horizontal position with even spacing
            full_width = self.display_surface.get_size()[0] 
            increment = full_width // self.attribute_nr
            left = (item * increment) + (increment - self.width) // 2
            
            top = self.display_surface.get_size()[1] * 0.1
            item = Item(left, top, self.width, self.height, index, self.font)
            self.item_list.append(item)
                
    def display(self):
        # Render upgrade menu with all stat items and keybind hints.
        self.input()
        self.selection_cooldown()
        
        # Draw all stat items
        for index, item in enumerate(self.item_list):
            name = self.attribute_names[index]
            value = self.player.get_value_by_index(index)
            max_value = self.max_values[index]
            cost = self.player.get_cost_by_index(index)
            
            item.display(self.display_surface, self.selection_index, name, value, max_value, cost)
        
        # Draw keybind hints
        self._draw_keybind_hints()
        self._draw_quit_hint()
        self._draw_notification()

    def consume_quit_request(self):
        if self.quit_requested:
            self.quit_requested = False
            return True
        return False

    def _draw_quit_hint(self):
        # Display hint for quitting the upgrade menu.
        hint_surface = self.font.render("Q - Quit", True, (255, 255, 255))
        hint_rect = hint_surface.get_rect(bottomright=(self.display_surface.get_size()[0] - 80, self.display_surface.get_size()[1] - 20))
        self.display_surface.blit(hint_surface, hint_rect)
        
    def _draw_keybind_hints(self):
        # Display save/load keybind hints.
        save_hint = self.font.render("Ctrl+S - Save Game", True, (255, 255, 255))
        load_hint = self.font.render("Ctrl+L - Load Game", True, (255, 255, 255))
        
        save_rect = save_hint.get_rect(
            bottomleft=(170, self.display_surface.get_size()[1] - 50)
        )
        load_rect = load_hint.get_rect(
            bottomleft=(170, self.display_surface.get_size()[1] - 20)
        )
        
        self.display_surface.blit(save_hint, save_rect)
        self.display_surface.blit(load_hint, load_rect)

    def _draw_notification(self):
        # Display save/load notification if active.
        current_time = pygame.time.get_ticks()
        if current_time < self.notification_time and self.notification_text:
            # Set up font
            font = pygame.font.Font(None, 36)
            text_surface = font.render(self.notification_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.display_surface.get_width() // 2, 50))
            
            # Draw background
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.display_surface, (0, 0, 0), bg_rect, border_radius=5)
            pygame.draw.rect(self.display_surface, (255, 255, 255), bg_rect, 2, border_radius=5)
            
            # Draw text
            self.display_surface.blit(text_surface, text_rect)


class Item: 
    def __init__(self, l, t, w, h, index, font):
        self.rect = pygame.Rect(l, t, w, h)
        self.index = index 
        self.font = font
    
    def display_names(self, surface, name, cost, selected):
        # Render stat name and upgrade cost.
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR
        
        title_surf = self.font.render(name, False, color)
        title_rect = title_surf.get_rect(midtop = self.rect.midtop + pygame.math.Vector2(0,20))
        
        cost_surf = self.font.render(f'{int(cost)}', False, color)
        cost_rect = cost_surf.get_rect(midbottom = self.rect.midbottom + pygame.math.Vector2(0,-20))
        
        surface.blit(title_surf, title_rect)
        surface.blit(cost_surf, cost_rect)
        
    def display_bar(self, surface, value, max_value, selected):
        # Draw vertical bar showing current stat level.
        top = self.rect.midtop + pygame.math.Vector2(0,60)
        bottom = self.rect.midbottom + pygame.math.Vector2(0,-60)
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR
        
        # Calculate bar fill based on stat percentage
        full_height = bottom[1] - top[1]
        relative_number = (value / max_value) * full_height
        value_rect = pygame.Rect(top[0] - 15, bottom[1] - relative_number, 30, 10)
        
        pygame.draw.line(surface, color, top, bottom, 5)
        pygame.draw.rect(surface, color, value_rect)
    
    def trigger(self, player):
        # Handle stat upgrade selection.
        stat_name = player.get_stat_name_by_index(self.index)
        if not stat_name:
            return
            
        upgrade_cost = player.upgrade_cost[stat_name]
        
        if player.exp >= upgrade_cost and player.stats[stat_name] < player.max_stats[stat_name]:
            player.exp -= upgrade_cost
            player.upgrade_stat(stat_name)
            # Upgrade successful, no sound will be played
            
    def display(self, surface, selection_num, name, value, max_value, cost):
        # Render complete upgrade item with background, border, and content.
        if self.index == selection_num: 
            pygame.draw.rect(surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        
        self.display_names(surface, name, cost, self.index == selection_num)
        self.display_bar(surface, value, max_value, self.index == selection_num)
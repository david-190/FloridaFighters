import pygame
from typing import List, Optional, Callable
from datetime import datetime

class SaveSlotMenu:
    def __init__(self, screen: pygame.Surface, save_manager, on_save_slot_selected: Callable[[int], None] = None, on_load_slot_selected: Callable[[int], None] = None):
        self.screen = screen
        self.save_manager = save_manager
        self.on_save_slot_selected = on_save_slot_selected
        self.on_load_slot_selected = on_load_slot_selected
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.selected_slot = 0
        self.max_slots = 5
        self.visible = False
        self.is_save_mode = True  # Track whether we're in save or load mode
        
    def show(self):
        """Show the save slot selection menu."""
        self.visible = True
        self.selected_slot = 0
        
    def hide(self):
        """Hide the save slot selection menu."""
        self.visible = False
        
    def set_mode(self, is_save_mode: bool):
        """Set whether the menu is in save or load mode."""
        self.is_save_mode = is_save_mode
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events for the save slot menu."""
        if not self.visible:
            return False
            
        if event.type == pygame.KEYDOWN:
            # Exit menu with Q or Escape
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                self.hide()
                return True
                
            # Navigation with arrow keys or WASD
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_slot = (self.selected_slot - 1) % self.max_slots
                return True
                
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_slot = (self.selected_slot + 1) % self.max_slots
                return True
                
            # Confirm with Space or Enter
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.is_save_mode and self.on_save_slot_selected:
                    self.on_save_slot_selected(self.selected_slot)
                elif not self.is_save_mode and self.on_load_slot_selected:
                    self.on_load_slot_selected(self.selected_slot)
                self.hide()
                return True
                
            # Direct slot selection with number keys 1-5 (optional)
            if pygame.K_1 <= event.key <= pygame.K_5:
                slot = event.key - pygame.K_1
                if slot < self.max_slots:
                    if self.is_save_mode and self.on_save_slot_selected:
                        self.on_save_slot_selected(slot)
                    elif not self.is_save_mode and self.on_load_slot_selected:
                        self.on_load_slot_selected(slot)
                    self.hide()
                    return True
                    
        return False
        
    def draw(self):
        """Draw the save slot selection menu."""
        if not self.visible:
            return
            
        # Semi-transparent background
        s = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))  # Black with alpha
        self.screen.blit(s, (0, 0))
        
        # Title
        title_text = "Select Save Slot" if self.is_save_mode else "Select Load Slot"
        title = self.font.render(title_text, True, (255, 255, 255))
        title_rect = title.get_rect(centerx=self.screen.get_width() // 2, top=100)
        self.screen.blit(title, title_rect)
        
        # Draw slots
        slot_width = 400
        slot_height = 70
        start_y = 200
        spacing = 20
        
        for i in range(self.max_slots):
            # Position and size of the slot
            rect = pygame.Rect(
                (self.screen.get_width() - slot_width) // 2,
                start_y + i * (slot_height + spacing),
                slot_width,
                slot_height
            )
            
            # Highlight selected slot
            if i == self.selected_slot:
                pygame.draw.rect(self.screen, (100, 100, 255), rect, 0, 10)
                pygame.draw.rect(self.screen, (200, 200, 255), rect, 3, 10)
            else:
                pygame.draw.rect(self.screen, (50, 50, 70), rect, 0, 10)
                pygame.draw.rect(self.screen, (100, 100, 120), rect, 2, 10)
            
            # Slot number
            slot_text = f"Slot {i + 1}"
            text_surf = self.font.render(slot_text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(midleft=(rect.left + 20, rect.centery))
            self.screen.blit(text_surf, text_rect)
            
            # Save info if exists
            save_info = self.save_manager.get_save_info(i)
            if save_info and 'timestamp' in save_info:
                # Format date
                try:
                    dt = datetime.fromisoformat(save_info['timestamp'])
                    date_str = dt.strftime('%Y-%m-%d %H:%M')
                except (ValueError, TypeError):
                    date_str = "Unknown date"
                    
                # Draw save info
                info_text = f"Saved: {date_str}"
                info_surf = self.small_font.render(info_text, True, (200, 200, 200))
                info_rect = info_surf.get_rect(
                    midleft=(rect.left + 120, rect.centery - 10)
                )
                self.screen.blit(info_surf, info_rect)
                
                # Draw player level if available
                if 'player_level' in save_info:
                    level_text = f"Level: {save_info['player_level']}"
                    level_surf = self.small_font.render(level_text, True, (200, 200, 200))
                    level_rect = level_surf.get_rect(
                        midleft=(rect.left + 120, rect.centery + 15)
                    )
                    self.screen.blit(level_surf, level_rect)
            else:
                # Empty slot
                empty_text = "(Empty Slot)"
                empty_surf = self.small_font.render(empty_text, True, (150, 150, 150))
                empty_rect = empty_surf.get_rect(
                    midleft=(rect.left + 120, rect.centery)
                )
                self.screen.blit(empty_surf, empty_rect)
import pygame
import sys
import os
from datetime import datetime
from settings import WATER_COLOR, FPS
from level import Level
from start_screen import StartScreen
from input_manager import InputManager
from save_manager import SaveManager
from save_slot_menu import SaveSlotMenu
from datetime import datetime

class Game:
    def __init__(self):
        # Initialize Pygame and create display window
        pygame.init()
        display_info = pygame.display.Info()
        self.screen = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.FULLSCREEN)
        pygame.display.set_caption('Aetherbound')
        self.clock = pygame.time.Clock()
        
        # Debug: Print current working directory
        print(f"Current working directory: {os.getcwd()}")
        
        # Track whether the game has transitioned from start screen to gameplay
        self.game_started = False
        
        self.start_screen = StartScreen(self.screen)
        
        # Level is instantiated after player starts the game
        self.level = None
        
        # Background music - starts when game begins
        self.main_sound = pygame.mixer.Sound('audio/main.ogg')
        self.main_sound.set_volume(0.5)

        # Unified input handler
        self.input_manager = InputManager(self.screen.get_size())
        
        # Save/load state
        self.save_notification_time = 0
        self.save_notification_text = ""
        self.save_slot = 0  # Current save slot (0-4)
        self.max_save_slots = 5  # Maximum number of save slots
        
        # Initialize save slot menu
        self.save_slot_menu = SaveSlotMenu(
            screen=self.screen,
            save_manager=SaveManager,
            on_save_slot_selected=self._on_save_slot_selected,
            on_load_slot_selected=self._on_load_slot_selected
        )
        
        # Ensure saves directory exists
        SaveManager.ensure_save_dir_exists()
        
    def run(self):
        """Main game loop handling events, updates, and rendering."""
        while True:
            # Process all events first
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Handle save slot menu input if visible (this takes priority)
                if self.save_slot_menu.visible:
                    if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                        if self.save_slot_menu.handle_event(event):
                            continue  # Event was handled by save slot menu
                
                # Handle start screen events
                if not self.game_started:
                    if event.type == pygame.KEYDOWN:
                        result = self.start_screen.handle_key(event.key)
                        if result == 'New Game':
                            self._start_gameplay(load_save=False, new_game=True)
                        elif result == 'Load Game':
                            # Show save slot menu for loading
                            self.save_slot_menu.set_mode(False)  # Set to load mode
                            self.save_slot_menu.show()
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
                        result = self.start_screen.handle_click(event.pos)
                        if result == 'New Game':
                            self._start_gameplay(load_save=False, new_game=True)
                        elif result == 'Load Game':
                            # Show save slot menu for loading
                            self.save_slot_menu.set_mode(False)  # Set to load mode
                            self.save_slot_menu.show()
                
                # Only pass events to input manager if save slot menu is not visible
                if not self.save_slot_menu.visible:
                    self.input_manager.process_event(event)

            # Check for load menu request (Control+L)
            if self.input_manager.consume_load_menu_request() and self.game_started:
                self.save_slot_menu.set_mode(False)  # Set to load mode
                self.save_slot_menu.show()
                
            # Update game state and handle state transitions
            self._handle_state_transitions()
            self.input_manager.update()
            self.screen.fill(WATER_COLOR)
            
            # Update start screen for hover effects
            if not self.game_started:
                self.start_screen.update()
            
            # Render current state
            if not self.game_started:
                self.start_screen.draw()
            else:
                self.level.run()
                
            # Draw save slot menu if visible
            self.save_slot_menu.draw()
                
            # Draw save/load notification if active
            self._draw_notification()
                
            pygame.display.update()
            self.clock.tick(FPS)

    def _handle_state_transitions(self):
        """Handle transitions between game states."""
        if not self.game_started:
            self.input_manager.set_gameplay_active(False)
            return

        # Handle player death
        if hasattr(self, 'level') and self.level and getattr(self.level, 'is_dead', False):
            # Get all events but don't consume them yet
            events = list(pygame.event.get(pygame.JOYBUTTONDOWN))
            keys = pygame.key.get_pressed()
            
            # Check for gamepad start button
            for event in events:
                if event.button == 7:  # Start button on most gamepads
                    # Only consume this specific event
                    pygame.event.clear(pygame.JOYBUTTONDOWN)
                    self._start_gameplay(load_save=False, new_game=True)
                    return
                # Let other events pass through
                pygame.event.post(event)
            
            # Check for keyboard space or enter
            if keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER] or keys[pygame.K_SPACE]:
                # Only consume these specific keys
                pygame.event.clear(pygame.KEYDOWN)  # Clear any keydown events to prevent double processing
                self._start_gameplay(load_save=False, new_game=True)
                return
                    
        # Regular gameplay input handling
        self.input_manager.set_gameplay_active(True)
        
        # Toggle menu with Escape if not already in menu and save slot menu is not visible
        if not self.save_slot_menu.visible and self.input_manager.consume_menu_toggle():
            self.level.toggle_menu()

    def _start_gameplay(self, load_save=False, new_game=False):
        # Stop any currently playing music
        self.main_sound.stop()
        
        # Save the current slot
        current_slot = self.save_slot
        
        # Reset game state
        self.game_started = True
        
        # Only delete save if this is explicitly a new game and we're not loading a save
        if new_game and not load_save:
            SaveManager.delete_save(current_slot)
        
        # Create new level instance
        self.level = Level(input_manager=self.input_manager, game=self)
        
        # Restore the save slot
        self.save_slot = current_slot
        
        # Try to load the save if requested and it exists
        if load_save and SaveManager.has_save(current_slot):
            self.load_game(current_slot)
        
        # Start music
        self.main_sound.play(loops=-1)

    
    def set_save_slot(self, slot: int) -> bool:
        """Change the current save slot."""
        if 0 <= slot < self.max_save_slots:
            self.save_slot = slot
            self.show_notification(f"Using Save Slot {slot + 1}")
            return True
        return False
            
    def save_game(self, slot=None):
        """Save the current game state to the specified slot."""
        if slot is not None:
            self.set_save_slot(slot)
            return self._perform_save()
        else:
            # Show save slot menu if no slot specified
            self.save_slot_menu.set_mode(True)  # Set to save mode
            self.save_slot_menu.show()
            return False
            
    def load_game(self, slot=None):
        """Load a game state from the specified slot."""
        if slot is not None:
            self.set_save_slot(slot)
        
        # If game hasn't started, start it first
        if not self.game_started:
            self._start_gameplay(load_save=True, new_game=False)
            return True
            
        # If already in game, perform the load
        return self._perform_load()
            
    def _on_save_slot_selected(self, slot: int):
        """Callback when a save slot is selected from the menu."""
        self.set_save_slot(slot)
        if self.game_started and self.level:
            # Always save when a slot is selected from the save menu
            self._perform_save()
                
    def _on_load_slot_selected(self, slot: int):
        """Callback when a load slot is selected from the menu."""
        self.set_save_slot(slot)
        if not self.game_started:
            # If we're on the start screen, start the game first
            self._start_gameplay(load_save=True, new_game=False)
        elif SaveManager.has_save(slot):
            # If we're in-game, just load the save
            self._perform_load()
            
    def _perform_save(self) -> bool:
        """Internal method to perform the actual save operation."""
        if not self.game_started or not self.level:
            return False
            
        game_state = self.level.get_state()
        if SaveManager.save_game(game_state, self.save_slot):
            self.show_notification(f"Game Saved (Slot {self.save_slot + 1})")
            return True
        return False
            
    def _perform_load(self) -> bool:
        """Internal method to perform the actual load operation."""
        if not self.game_started or not self.level:
            return False
                
        game_state = SaveManager.load_game(self.save_slot)
        if game_state:
            self.level.load_state(game_state)
            self.show_notification(f"Game Loaded (Slot {self.save_slot + 1})")
            return True
        else:
            self.show_notification("No Save Found")
            return False
            
    def show_notification(self, text, duration=2000):
        """Show a temporary notification on screen."""
        self.save_notification_text = text
        self.save_notification_time = pygame.time.get_ticks() + duration
        
    def _draw_notification(self):
        """Draw the current notification if active."""
        current_time = pygame.time.get_ticks()
        if current_time < self.save_notification_time and self.save_notification_text:
            # Set up font
            font = pygame.font.Font(None, 36)
            text_surface = font.render(self.save_notification_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, 50))
            
            # Draw background
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect, border_radius=5)
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 2, border_radius=5)
            
            # Draw text
            self.screen.blit(text_surface, text_rect)

if __name__ == "__main__":
    game = Game()
    game.run()
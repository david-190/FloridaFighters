import pygame
import sys
from settings import WATER_COLOR, FPS

from level import Level
from start_screen import StartScreen
from input_manager import InputManager

class Game:
    def __init__(self):
        # Initialize Pygame and create display window
        pygame.init()
        display_info = pygame.display.Info()
        self.screen = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.FULLSCREEN)
        pygame.display.set_caption('Aetherbound')
        self.clock = pygame.time.Clock()
        
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
        
    def run(self):
        """Main game loop handling events, updates, and rendering."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.input_manager.process_event(event)

            self.input_manager.update()

            self.screen.fill(WATER_COLOR)
            self._handle_state_transitions()
            
            # Render either start screen or active gameplay
            if not self.game_started:
                self.start_screen.draw()
            else:
                self.level.run()
                
            pygame.display.update()
            self.clock.tick(FPS)

    def _handle_state_transitions(self):
        if not self.game_started:
            if self.input_manager.consume_start_request():
                self._start_gameplay()
            else:
                self.input_manager.set_gameplay_active(False)
            return

        # Gameplay active
        self.input_manager.set_gameplay_active(True)

        if self.level.is_dead:
            if self.input_manager.consume_start_request():
                self.level = Level(input_manager=self.input_manager)
            return

        if self.input_manager.consume_menu_toggle():
            self.level.toggle_menu()

    def _start_gameplay(self):
        self.game_started = True
        self.level = Level(input_manager=self.input_manager)
        self.main_sound.play(loops=-1)

    
if __name__ == "__main__":
    game = Game()
    game.run()
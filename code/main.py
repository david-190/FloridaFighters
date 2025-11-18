import pygame
import sys
from settings import WIDTH, HEIGTH, WATER_COLOR, FPS
from level import Level
from start_screen import StartScreen

class Game:
    def __init__(self):
        # Initialize Pygame and create display window
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
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
        
    def run(self):
        """Main game loop handling events, updates, and rendering."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if not self.game_started:
                        # Space key starts the game from the start screen
                        if event.key == pygame.K_SPACE:
                            self.game_started = True
                            self.level = Level()
                            self.main_sound.play(loops = -1)
                    else:
                        # Space key restarts the level after player death
                        if self.level.is_dead:
                            if event.key == pygame.K_SPACE:
                                self.level = Level()
                                continue
                        # Escape key toggles the in-game menu
                        if event.key == pygame.K_ESCAPE:
                            self.level.toggle_menu()

            self.screen.fill(WATER_COLOR)
            
            # Render either start screen or active gameplay
            if not self.game_started:
                self.start_screen.draw()
            else:
                self.level.run()
                
            pygame.display.update()
            self.clock.tick(FPS)
    
if __name__ == "__main__":
    game = Game()
    game.run()
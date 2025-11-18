import pygame
from settings import UI_FONT, UI_FONT_SIZE, WIDTH, HEIGTH, TEXT_COLOR

class StartScreen:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        
        # Load and scale the portrait image
        original_portrait = pygame.image.load('graphics/menu/portrait.jpg').convert_alpha()
        
        # Calculate scaling to fit nicely in the window (e.g., 40% of screen height)
        target_height = int(HEIGTH * 0.5)  # 50% of screen height
        aspect_ratio = original_portrait.get_width() / original_portrait.get_height()
        target_width = int(target_height * aspect_ratio)
        
        # Scale the image
        self.portrait_img = pygame.transform.scale(original_portrait, (target_width, target_height))
        self.portrait_rect = self.portrait_img.get_rect(center=(WIDTH//2, HEIGTH//2 - 80))
        
        # Text setup
        self.text = 'Press SPACE to start'
        self.text_surf = self.font.render(self.text, True, TEXT_COLOR)
        self.text_rect = self.text_surf.get_rect(center=(WIDTH//2, HEIGTH//2 + 160))

    def draw(self):
        # Dim background
        overlay = pygame.Surface((WIDTH, HEIGTH))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.display_surface.blit(overlay, (0, 0))
        
        # Draw portrait
        self.display_surface.blit(self.portrait_img, self.portrait_rect)
        
        # Draw text
        self.display_surface.blit(self.text_surf, self.text_rect)
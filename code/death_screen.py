import pygame
from settings import UI_FONT, UI_FONT_SIZE, WIDTH, HEIGTH, TEXT_COLOR

class DeathScreen:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.face_img = pygame.image.load('graphics/player/faceset/faceset.png').convert_alpha()
        self.face_rect = self.face_img.get_rect(center=(WIDTH//2, HEIGTH//2 - 80))
        self.text = 'You Died! Press SPACE to restart.'
        self.text_surf = self.font.render(self.text, True, TEXT_COLOR)
        self.text_rect = self.text_surf.get_rect(center=(WIDTH//2, HEIGTH//2 + 60))

    def draw(self):
        """Render death screen with semi-transparent overlay."""
        # Create darkened overlay
        overlay = pygame.Surface((WIDTH, HEIGTH))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        self.display_surface.blit(overlay, (0,0))
        
        self.display_surface.blit(self.face_img, self.face_rect)
        self.display_surface.blit(self.text_surf, self.text_rect)
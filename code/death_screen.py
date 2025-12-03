import pygame
from settings import UI_FONT, UI_FONT_SIZE, TEXT_COLOR

class DeathScreen:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.face_img = pygame.image.load('graphics/player/faceset/faceset.png').convert_alpha()
        screen_width, screen_height = self.display_surface.get_size()
        self.face_rect = self.face_img.get_rect(center=(screen_width//2, screen_height//2 - 80))
        self.text = 'You Died! Press SPACE / Start / Tap to restart.'
        self.text_surf = self.font.render(self.text, True, TEXT_COLOR)
        self.text_rect = self.text_surf.get_rect(center=(screen_width//2, screen_height//2 + 60))

    def draw(self):
        # Create darkened overlay
        overlay = pygame.Surface(self.display_surface.get_size())
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        
        self.display_surface.blit(overlay, (0,0))
        
        self.display_surface.blit(self.face_img, self.face_rect)
        self.display_surface.blit(self.text_surf, self.text_rect)
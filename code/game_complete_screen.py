import pygame
from settings import UI_FONT, UI_FONT_SIZE, TEXT_COLOR


class GameCompleteScreen:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.big_font = pygame.font.Font(UI_FONT, UI_FONT_SIZE * 2)

        self._update_layout()

    def _update_layout(self):
        width, height = self.display_surface.get_size()
        self.title_surf = self.big_font.render('Congratulations!', True, TEXT_COLOR)
        self.title_rect = self.title_surf.get_rect(center=(width // 2, height // 2 - 80))

        self.subtitle = 'All enemies are defeated.'
        self.subtitle_surf = self.font.render(self.subtitle, True, TEXT_COLOR)
        self.subtitle_rect = self.subtitle_surf.get_rect(center=(width // 2, height // 2))

        self.prompt = 'Quit: Q / LB / Tap top-left'
        self.prompt_surf = self.font.render(self.prompt, True, TEXT_COLOR)
        self.prompt_rect = self.prompt_surf.get_rect(center=(width // 2, height // 2 + 80))

    def draw(self):
        # Ensure layout matches current screen size (in case of resize)
        self._update_layout()

        overlay = pygame.Surface(self.display_surface.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.display_surface.blit(overlay, (0, 0))

        self.display_surface.blit(self.title_surf, self.title_rect)
        self.display_surface.blit(self.subtitle_surf, self.subtitle_rect)
        self.display_surface.blit(self.prompt_surf, self.prompt_rect)

import pygame
from settings import UI_FONT, UI_FONT_SIZE, TEXT_COLOR, UI_BG_COLOR, UI_BORDER_COLOR, UI_BORDER_COLOR_ACTIVE, UI_FONT_SIZE_LARGE

class StartScreen:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.title_font = pygame.font.Font(UI_FONT, UI_FONT_SIZE_LARGE)
        
        self.screen_width, self.screen_height = self.display_surface.get_size()
        self.menu_options = ['New Game', 'Load Game']
        self.selected_index = 0
        self.option_rects = []
        
        # Load and scale the portrait image
        original_portrait = pygame.image.load('graphics/menu/portrait.jpg').convert_alpha()
        
        # Calculate scaling to fit nicely in the window (e.g., 40% of screen height)
        target_height = int(self.screen_height * 0.4)
        aspect_ratio = original_portrait.get_width() / original_portrait.get_height()
        target_width = int(target_height * aspect_ratio)
        
        # Scale the image
        self.portrait_img = pygame.transform.scale(original_portrait, (target_width, target_height))
        self.portrait_rect = self.portrait_img.get_rect(center=(self.screen_width//2, self.screen_height//3))
        
        # Game title
        self.title_surf = self.title_font.render('AETHERBOUND', True, TEXT_COLOR)
        self.title_rect = self.title_surf.get_rect(center=(self.screen_width//2, self.screen_height//6))
        
        # Create menu options
        self._create_menu_options()
        
    def _create_menu_options(self):
        self.option_rects = []
        option_height = 60
        start_y = self.screen_height // 2 + 50
        
        for i, option in enumerate(self.menu_options):
            # Create a rect for each option
            rect = pygame.Rect(0, 0, 300, 50)
            rect.center = (self.screen_width//2, start_y + i * (option_height + 20))
            self.option_rects.append(rect)
    
    def draw(self):
        # Dim background
        overlay = pygame.Surface(self.display_surface.get_size())
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.display_surface.blit(overlay, (0, 0))
        
        # Draw title
        self.display_surface.blit(self.title_surf, self.title_rect)
        
        # Draw portrait
        self.display_surface.blit(self.portrait_img, self.portrait_rect)
        
        # Draw menu options
        for i, (option, rect) in enumerate(zip(self.menu_options, self.option_rects)):
            # Draw button background
            bg_color = UI_BORDER_COLOR_ACTIVE if i == self.selected_index else UI_BG_COLOR
            border_color = UI_BORDER_COLOR_ACTIVE
            
            pygame.draw.rect(self.display_surface, bg_color, rect, border_radius=10)
            pygame.draw.rect(self.display_surface, border_color, rect, 3, border_radius=10)
            
            # Draw option text
            text_surf = self.font.render(option, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=rect.center)
            self.display_surface.blit(text_surf, text_rect)
    
    def update(self):
        # Handle mouse hover
        mouse_pos = pygame.mouse.get_pos()
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_index = i
                break
    
    def handle_click(self, pos):
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(pos):
                return self.menu_options[i]
        return None
        
    def handle_key(self, key):
        if key == pygame.K_UP or key == pygame.K_w:
            self.selected_index = (self.selected_index - 1) % len(self.menu_options)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.selected_index = (self.selected_index + 1) % len(self.menu_options)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            return self.menu_options[self.selected_index]
        return None
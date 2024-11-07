import pygame
from typing import Optional, Tuple

class TextInput:
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font):
        self.screen = screen
        self.font = font
        self.text = ""
        self.active = False
        self.position = (0, 0)
        
        # Colors
        self.bg_color = (240, 240, 240)
        self.text_color = (0, 0, 0)
        self.border_color = (100, 100, 100)
        
        # Input box dimensions
        self.width = 300
        self.height = 40
        self.padding = 5
        
        # Label
        self.label = "Enter Building Name:"
        self.label_color = (50, 50, 50)

    def activate(self, position: Tuple[int, int]):
        """Activate text input at given position"""
        self.active = True
        self.text = ""
        # Center the input box on the position
        self.position = (
            position[0] - self.width // 2,
            position[1] - self.height // 2
        )

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle keyboard events. Returns the final text when enter is pressed."""
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                final_text = self.text
                self.active = False
                self.text = ""
                return final_text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                self.text = ""
                return None
            else:
                # Only add printable characters
                if event.unicode.isprintable():
                    self.text += event.unicode
        return None

    def draw(self):
        """Draw the text input box if active"""
        if not self.active:
            return

        # Draw semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 128), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))

        # Draw input box background
        input_rect = pygame.Rect(
            self.position[0],
            self.position[1],
            self.width,
            self.height
        )
        pygame.draw.rect(self.screen, self.bg_color, input_rect)
        pygame.draw.rect(self.screen, self.border_color, input_rect, 2)

        # Draw label above input box
        label_surface = self.font.render(self.label, True, self.label_color)
        label_pos = (
            self.position[0],
            self.position[1] - 30
        )
        self.screen.blit(label_surface, label_pos)

        # Draw current text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_pos = (
            self.position[0] + self.padding,
            self.position[1] + (self.height - text_surface.get_height()) // 2
        )
        self.screen.blit(text_surface, text_pos)

        # Draw cursor
        if pygame.time.get_ticks() % 1000 < 500:  # Blink cursor
            cursor_x = text_pos[0] + text_surface.get_width()
            pygame.draw.line(
                self.screen,
                self.text_color,
                (cursor_x, text_pos[1] + 5),
                (cursor_x, text_pos[1] + text_surface.get_height() - 5),
                2
            ) 
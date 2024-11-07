import pygame

class ConsolePanel:
    def __init__(self, screen: pygame.Surface, width: int, height: int, map_editor):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.map_editor = map_editor  # Store reference to map_editor
        
        # Console colors
        self.bg_color = (240, 240, 240)  # Light gray
        self.text_color = (50, 50, 50)   # Dark gray
        self.header_color = (70, 70, 70)  # Darker gray
        
        # Different instruction sets for different modes
        self.edit_instructions = [
            "Edit Mode Controls:",
            "Left Click: Add building node",
            "Alt + Left Click: Add waypoint",
            "Right Click: Create edge",
            "Shift + Right Click: Remove",
            "E: Switch to Navigation Mode",
            "M: Toggle Map Type",
            "A: Toggle Accessibility",
            "Ctrl+S: Save Map",
            "Ctrl+L: Load Map",
            "ESC: Quit"
        ]
        
        self.navigation_instructions = [
            "Navigation Mode Controls:",
            "Left Click: Select start/end",
            "R: Reset selection",
            "P: Toggle path type",
            "  (Fastest/Accessible)",
            "E: Switch to Edit Mode",
            "ESC: Quit"
        ]

    def draw(self):
        # Draw console background
        pygame.draw.rect(self.screen, self.bg_color, (0, 0, self.width, self.height))
        pygame.draw.line(self.screen, (200, 200, 200), (self.width, 0), 
                        (self.width, self.height), 2)

        # Draw header
        header = self.font.render("CSUF Navigator", True, self.header_color)
        self.screen.blit(header, (10, 20))

        # Choose which instructions to display based on mode
        current_instructions = self.edit_instructions if getattr(self.map_editor, 'edit_mode', True) else self.navigation_instructions

        # Draw instructions
        y = 70
        for instruction in current_instructions:
            text = self.small_font.render(instruction, True, self.text_color)
            self.screen.blit(text, (10, y))
            y += 25

        # Draw accessibility status
        status_text = f"Accessibility: {'ON' if self.map_editor.is_accessible else 'OFF'}"
        status = self.small_font.render(status_text, True, self.text_color)
        self.screen.blit(status, (10, y))
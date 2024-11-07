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

        # Add dropdown menu properties
        self.dropdown_open = False
        self.dropdown_rect = pygame.Rect(10, 280, 180, 30)  # Position below existing controls
        self.algorithm_options = [
            "Dijkstra's Algorithm",
            "Breadth-First Search",
            "Depth-First Search"
        ]
        self.selected_algorithm = "Dijkstra's Algorithm"
        self.option_height = 30

    def handle_click(self, pos):
        """Handle clicks on the dropdown menu"""
        if self.dropdown_rect.collidepoint(pos):
            self.dropdown_open = not self.dropdown_open
        elif self.dropdown_open:
            # Check if clicked on an option
            for i, _ in enumerate(self.algorithm_options):
                option_rect = pygame.Rect(
                    self.dropdown_rect.x,
                    self.dropdown_rect.y + (i + 1) * self.option_height,
                    self.dropdown_rect.width,
                    self.option_height
                )
                if option_rect.collidepoint(pos):
                    self.selected_algorithm = self.algorithm_options[i]
                    self.dropdown_open = False
                    return True
        return False

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

        # Draw algorithm selector dropdown
        if not getattr(self.map_editor, 'edit_mode', True):  # Only show in navigation mode
            pygame.draw.rect(self.screen, (255, 255, 255), self.dropdown_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), self.dropdown_rect, 2)
            
            # Draw selected algorithm
            text = self.small_font.render(self.selected_algorithm, True, self.text_color)
            text_rect = text.get_rect(midleft=(self.dropdown_rect.x + 5, self.dropdown_rect.centery))
            self.screen.blit(text, text_rect)
            
            # Draw dropdown arrow
            arrow_points = [
                (self.dropdown_rect.right - 20, self.dropdown_rect.centery - 5),
                (self.dropdown_rect.right - 10, self.dropdown_rect.centery + 5),
                (self.dropdown_rect.right - 30, self.dropdown_rect.centery + 5)
            ]
            pygame.draw.polygon(self.screen, self.text_color, arrow_points)
            
            # Draw options if dropdown is open
            if self.dropdown_open:
                for i, option in enumerate(self.algorithm_options):
                    option_rect = pygame.Rect(
                        self.dropdown_rect.x,
                        self.dropdown_rect.y + (i + 1) * self.option_height,
                        self.dropdown_rect.width,
                        self.option_height
                    )
                    pygame.draw.rect(self.screen, (255, 255, 255), option_rect)
                    pygame.draw.rect(self.screen, (100, 100, 100), option_rect, 1)
                    
                    text = self.small_font.render(option, True, self.text_color)
                    text_rect = text.get_rect(midleft=(option_rect.x + 5, option_rect.centery))
                    self.screen.blit(text, text_rect)
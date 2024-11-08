import pygame  # Import the pygame library for graphics and game development

class ConsolePanel:
    def __init__(self, screen: pygame.Surface, width: int, height: int, map_editor):
        # Initialize the console panel with screen, dimensions, and map editor reference
        self.screen = screen  # The surface where the console will be drawn
        self.width = width  # Width of the console panel
        self.height = height  # Height of the console panel
        self.font = pygame.font.Font(None, 24)  # Font for rendering main text
        self.small_font = pygame.font.Font(None, 20)  # Font for rendering smaller text
        self.map_editor = map_editor  # Reference to the map editor for mode checking
        self.nav_handler = None  # Navigation handler, initialized as None
        
        # Console colors
        self.bg_color = (240, 240, 240)  # Background color of the console (light gray)
        self.text_color = (50, 50, 50)   # Color of the text (dark gray)
        self.header_color = (70, 70, 70)  # Color of the header text (darker gray)
        
        # Different instruction sets for different modes
        self.edit_instructions = [  # Instructions for edit mode
            "Edit Mode Controls:",
            "E: Switch to Navigation Mode",
            "Left Click: Add building node",
            "Alt + Left Click: Add waypoint",
            "Right Click: Create edge",
            "Shift + Right Click: Remove",
            "M: Toggle Map Type",
            "A: Toggle Accessibility Editing",
            "Ctrl+S: Save Map",
            "Ctrl+L: Load Map",
            "ESC: Quit"
        ]
        
        self.navigation_instructions = [  # Instructions for navigation mode
            "Navigation Mode Controls:",
            "E: Switch to Edit Mode",
            "Left Click: Select start/end",
            "R: Reset selection",
            "A: Toggle Accessibility",
            "ESC: Quit"
        ]

        # Dropdown menu properties
        self.dropdown_open = False  # Flag to check if the dropdown menu is open
        self.dropdown_rect = pygame.Rect(10, 280, 180, 30)  # Position of the dropdown menu
        self.algorithm_options = [  # List of algorithm options for selection
            "Dijkstra's Algorithm",
            "Breadth-First Search",
            "Depth-First Search"
        ]
        self.selected_algorithm = "Dijkstra's Algorithm"  # Default selected algorithm
        self.option_height = 30  # Height of each dropdown option

        self.accessibility_editing = False  # Flag for accessibility editing mode
        self.nav_accessibility = False  # Flag for navigation accessibility

    def handle_click(self, pos):
        """Handle clicks on the dropdown menu"""
        # Check if the click is within the dropdown rectangle
        if self.dropdown_rect.collidepoint(pos):
            self.dropdown_open = not self.dropdown_open  # Toggle dropdown open state
        elif self.dropdown_open:  # If dropdown is open, check for option selection
            # Iterate through algorithm options to check for selection
            for i, _ in enumerate(self.algorithm_options):
                option_rect = pygame.Rect(
                    self.dropdown_rect.x,
                    self.dropdown_rect.y + (i + 1) * self.option_height,  # Position of each option
                    self.dropdown_rect.width,
                    self.option_height
                )
                if option_rect.collidepoint(pos):  # Check if the click is on this option
                    self.selected_algorithm = self.algorithm_options[i]  # Update selected algorithm
                    self.dropdown_open = False  # Close the dropdown
                    return True  # Indicate that an option was selected
        return False  # No option was selected

    def draw(self):
        """Draw the console panel and its contents"""
        # Draw console background
        pygame.draw.rect(self.screen, self.bg_color, (0, 0, self.width, self.height))  # Draw background rectangle
        pygame.draw.line(self.screen, (200, 200, 200), (self.width, 0), 
                        (self.width, self.height), 2)  # Draw vertical line separating console from map

        # Draw header
        header = self.font.render("CSUF Navigator", True, self.header_color)  # Render header text
        self.screen.blit(header, (10, 20))  # Blit header onto the screen

        # Check if in edit mode
        if getattr(self.map_editor, 'edit_mode', True):
            # If in accessibility editing mode, show special instructions
            if self.map_editor.is_accessible:  # Check if accessibility editing is active
                instructions = [  # Instructions specific to accessibility editing
                    "Accessibility Editing Mode:",
                    "",
                    "Click on paths to toggle",
                    "their accessibility status",
                    "",
                    "Yellow: Regular Path",
                    "Green: Accessible Path",
                    "",
                    "Ctrl+S: Save Map",
                    "Ctrl+L: Load Map",
                    "A: Exit Accessibility Editing"
                ]
                y_offset = 70  # Initial vertical offset for drawing instructions
                for line in instructions:  # Draw each instruction line
                    text = self.small_font.render(line, True, self.text_color)  # Render instruction text
                    self.screen.blit(text, (15, y_offset))  # Blit instruction text onto the screen
                    y_offset += 25  # Increment vertical offset for next line
                return  # Exit after drawing accessibility instructions

        # Determine which set of instructions to display
        current_instructions = self.edit_instructions if getattr(self.map_editor, 'edit_mode', True) else self.navigation_instructions

        # Draw instructions
        y = 70  # Reset vertical position for drawing instructions
        for instruction in current_instructions:  # Iterate through current instructions
            text = self.small_font.render(instruction, True, self.text_color)  # Render instruction text
            self.screen.blit(text, (10, y))  # Blit instruction text onto the screen
            y += 25  # Increment vertical offset for next instruction

        # Draw accessibility status in navigation mode
        if not getattr(self.map_editor, 'edit_mode', True) and hasattr(self.nav_handler, 'accessibility'):
            status_text = f"Accessibility Mode: {'ON' if self.nav_handler.accessibility else 'OFF'}"  # Status text based on accessibility
            status = self.small_font.render(status_text, True, 
                (0, 150, 0) if self.nav_handler.accessibility else self.text_color)  # Green if accessibility is ON
            self.screen.blit(status, (10, y))  # Blit accessibility status onto the screen
            y += 25  # Increment vertical offset for next element

        # Draw algorithm selector dropdown in navigation mode
        if not getattr(self.map_editor, 'edit_mode', True):
            pygame.draw.rect(self.screen, (255, 255, 255), self.dropdown_rect)  # Draw dropdown background
            pygame.draw.rect(self.screen, (100, 100, 100), self.dropdown_rect, 2)  # Draw dropdown border
            
            # Draw selected algorithm
            text = self.small_font.render(self.selected_algorithm, True, self.text_color)  # Render selected algorithm text
            text_rect = text.get_rect(midleft=(self.dropdown_rect.x + 5, self.dropdown_rect.centery))  # Position text in dropdown
            self.screen.blit(text, text_rect)  # Blit selected algorithm text onto the screen
            
            # Draw dropdown arrow
            arrow_points = [  # Define points for the dropdown arrow
                (self.dropdown_rect.right - 20, self.dropdown_rect.centery - 5),
                (self.dropdown_rect.right - 10, self.dropdown_rect.centery + 5),
                (self.dropdown_rect.right - 30, self.dropdown_rect.centery + 5)
            ]
            pygame.draw.polygon(self.screen, self.text_color, arrow_points)  # Draw the dropdown arrow
            
            # Draw options if dropdown is open
            if self.dropdown_open:  # Check if the dropdown is open
                for i, option in enumerate(self.algorithm_options):  # Iterate through algorithm options
                    option_rect = pygame.Rect(
                        self.dropdown_rect.x,
                        self.dropdown_rect.y + (i + 1) * self.option_height,  # Position of each option
                        self.dropdown_rect.width,
                        self.option_height
                    )
                    pygame.draw.rect(self.screen, (255, 255, 255), option_rect)  # Draw option background
                    pygame.draw.rect(self.screen, (100, 100, 100), option_rect, 1)  # Draw option border
                    
                    text = self.small_font.render(option, True, self.text_color)  # Render option text
                    text_rect = text.get_rect(midleft=(option_rect.x + 5, option_rect.centery))  # Position text in option
                    self.screen.blit(text, text_rect)  # Blit option text onto the screen
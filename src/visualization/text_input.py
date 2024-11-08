import pygame  # Import the pygame library for rendering graphics
from typing import Optional, Tuple  # Importing types for optional return and tuple

class TextInput:
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font):
        """Initialize the TextInput object with screen and font."""
        self.screen = screen  # Store the screen surface for drawing
        self.font = font  # Store the font for rendering text
        self.text = ""  # Initialize the text input as an empty string
        self.active = False  # Flag to check if the input is active
        self.position = (0, 0)  # Initial position of the input box
        
        # Colors for the input box and text
        self.bg_color = (240, 240, 240)  # Background color of the input box
        self.text_color = (0, 0, 0)  # Color of the text
        self.border_color = (100, 100, 100)  # Color of the input box border
        
        # Input box dimensions
        self.width = 300  # Width of the input box
        self.height = 40  # Height of the input box
        self.padding = 5  # Padding for text inside the input box
        
        # Label for the input box
        self.label = "Enter Building Name:"  # Text label for the input box
        self.label_color = (50, 50, 50)  # Color of the label text

    def activate(self, position: Tuple[int, int]):
        """Activate text input at given position."""
        self.active = True  # Set the input to active
        self.text = ""  # Clear any existing text
        # Center the input box on the specified position
        self.position = (
            position[0] - self.width // 2,  # Center horizontally
            position[1] - self.height // 2  # Center vertically
        )

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle keyboard events. Returns the final text when enter is pressed."""
        if not self.active:  # If the input is not active, ignore events
            return None

        if event.type == pygame.KEYDOWN:  # Check if a key is pressed
            if event.key == pygame.K_RETURN:  # If the Enter key is pressed
                final_text = self.text  # Store the current text
                self.active = False  # Deactivate the input
                self.text = ""  # Clear the text for future input
                return final_text  # Return the final text
            elif event.key == pygame.K_BACKSPACE:  # If Backspace is pressed
                self.text = self.text[:-1]  # Remove the last character
            elif event.key == pygame.K_ESCAPE:  # If Escape is pressed
                self.active = False  # Deactivate the input
                self.text = ""  # Clear the text
                return None  # Return None to indicate cancellation
            else:
                # Only add printable characters to the text
                if event.unicode.isprintable():  # Check if the character is printable
                    self.text += event.unicode  # Append the character to the text
        return None  # Return None if no relevant event occurred

    def draw(self):
        """Draw the text input box if active."""
        if not self.active:  # If the input is not active, do not draw
            return

        # Draw a semi-transparent overlay to focus on the input box
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)  # Create an overlay surface
        pygame.draw.rect(overlay, (0, 0, 0, 128), overlay.get_rect())  # Draw a semi-transparent rectangle
        self.screen.blit(overlay, (0, 0))  # Blit the overlay onto the screen

        # Draw the input box background
        input_rect = pygame.Rect(
            self.position[0],  # X position
            self.position[1],  # Y position
            self.width,  # Width of the input box
            self.height  # Height of the input box
        )
        pygame.draw.rect(self.screen, self.bg_color, input_rect)  # Draw the background
        pygame.draw.rect(self.screen, self.border_color, input_rect, 2)  # Draw the border

        # Draw the label above the input box
        label_surface = self.font.render(self.label, True, self.label_color)  # Render the label text
        label_pos = (
            self.position[0],  # X position of the label
            self.position[1] - 30  # Y position of the label, above the input box
        )
        self.screen.blit(label_surface, label_pos)  # Blit the label onto the screen

        # Draw the current text inside the input box
        text_surface = self.font.render(self.text, True, self.text_color)  # Render the current text
        text_pos = (
            self.position[0] + self.padding,  # X position with padding
            self.position[1] + (self.height - text_surface.get_height()) // 2  # Center vertically
        )
        self.screen.blit(text_surface, text_pos)  # Blit the text onto the screen

        # Draw the blinking cursor
        if pygame.time.get_ticks() % 1000 < 500:  # Check if it's time to blink the cursor
            cursor_x = text_pos[0] + text_surface.get_width()  # Calculate cursor position
            pygame.draw.line(
                self.screen,
                self.text_color,  # Color of the cursor
                (cursor_x, text_pos[1] + 5),  # Start position of the cursor
                (cursor_x, text_pos[1] + text_surface.get_height() - 5),  # End position of the cursor
                2  # Width of the cursor line
            ) 
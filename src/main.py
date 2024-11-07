import pygame  # Import the pygame library for game development
from visualization.map_handler import MapHandler  # Import the MapHandler for managing the map display
from visualization.console_panel import ConsolePanel  # Import the ConsolePanel for UI elements
from visualization.text_input import TextInput  # Import the TextInput for handling user input
from data.map_editor import MapEditor  # Import the MapEditor for editing the map
from algorithms.graph import GraphManager  # Import the GraphManager for managing graph algorithms
from navigation.nav_handler import NavigationHandler  # Import the NavigationHandler for navigation logic

class CSUFNavigator:
    def __init__(self):
        pygame.init()  # Initialize all imported pygame modules
        self.map_handler = MapHandler()  # Create an instance of MapHandler
        self.map_editor = MapEditor()  # Create an instance of MapEditor
        self.console_panel = ConsolePanel(
            self.map_handler.screen,  # Pass the screen from map_handler
            self.map_handler.console_width,  # Pass the console width
            self.map_handler.window_height,  # Pass the window height
            self.map_editor  # Pass the map editor instance
        )
        self.text_input = TextInput(self.map_handler.screen, pygame.font.Font(None, 32))  # Create a text input field
        self.graph_manager = GraphManager(self.map_editor.campus_data)  # Create a graph manager with campus data
        self.nav_handler = NavigationHandler(self.graph_manager)  # Create a navigation handler with the graph manager
        self.edit_mode = True  # Set the initial mode to edit mode
        self.running = True  # Set the running state to true

    def run(self):
        """Main loop to run the navigator."""
        while self.running:  # Continue running while the navigator is active
            self._handle_events()  # Handle user input events
            self._update_display()  # Update the display

    def _handle_events(self):
        """Handle all events from the pygame event queue."""
        for event in pygame.event.get():  # Loop through all events
            if event.type == pygame.QUIT:  # Check if the quit event is triggered
                self.running = False  # Stop the main loop
            elif event.type == pygame.KEYDOWN:  # Check for key presses
                # Handle text input first
                if self.text_input.active:  # If text input is active
                    result = self.text_input.handle_event(event)  # Handle the event
                    if result is not None:  # If Enter was pressed
                        if result:  # If text wasn't empty
                            self.map_editor.complete_node_creation(result)  # Complete node creation with the input
                else:
                    self._handle_keypress(event.key)  # Handle key presses
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Check for mouse button presses
                if not self.text_input.active:  # If text input is not active
                    self._handle_mouse_click(event)  # Handle mouse click events
            elif event.type == pygame.MOUSEMOTION:  # Check for mouse motion events
                self.mouse_pos = event.pos  # Update mouse position

    def _handle_keypress(self, key):
        """Handle key presses for various commands."""
        if key == pygame.K_ESCAPE:  # If the Escape key is pressed
            self.running = False  # Stop the main loop
        elif key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:  # If Ctrl + S is pressed
            self.map_editor.save_map()  # Save the current map
            print("Map saved!")  # Print confirmation
        elif key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:  # If Ctrl + L is pressed
            self.map_editor.load_map()  # Load a saved map
            print("Map loaded!")  # Print confirmation
        elif key == pygame.K_e:  # If the E key is pressed
            self.edit_mode = not self.edit_mode  # Toggle edit mode
            self.map_editor.edit_mode = self.edit_mode  # Update the map editor's edit mode
            print(f"Edit mode: {'ON' if self.edit_mode else 'OFF'}")  # Print current edit mode status
        elif key == pygame.K_m:  # If the M key is pressed
            self.map_handler.toggle_map()  # Toggle the map display
        elif key == pygame.K_a:  # If the A key is pressed
            self.map_editor.is_accessible = not self.map_editor.is_accessible  # Toggle accessibility mode
            print(f"Accessibility mode: {'ON' if self.map_editor.is_accessible else 'OFF'}")  # Print current accessibility status
        elif not self.edit_mode:  # If not in edit mode
            if key == pygame.K_r:  # If the R key is pressed
                self.nav_handler.reset_selection()  # Reset the current selection
            elif key == pygame.K_p:  # If the P key is pressed
                self.nav_handler.toggle_path_type()  # Toggle the path type

    def _handle_mouse_click(self, event):
        """Handle mouse click events for node and edge creation."""
        map_pos = self.map_handler.screen_to_map_coords(event.pos)  # Convert screen position to map coordinates
        
        if map_pos[0] >= 0 and map_pos[0] <= self.map_handler.map_width:  # Check if the click is within map bounds
            normalized_pos = self.map_handler.map_to_normalized_coords(map_pos)  # Normalize the map position
            
            if self.edit_mode:  # If in edit mode
                # Existing edit mode code
                shift_held = pygame.key.get_mods() & pygame.KMOD_SHIFT  # Check if Shift is held
                alt_held = pygame.key.get_mods() & pygame.KMOD_ALT  # Check if Alt is held
                
                if pygame.mouse.get_pressed()[0] and not alt_held:  # Left click for building
                    self.map_editor._handle_node_creation(normalized_pos, event.pos)  # Handle node creation
                    if self.map_editor.pending_node:  # If there is a pending node
                        self.text_input.activate(event.pos)  # Activate text input for naming
                else:
                    self.map_editor.handle_click(map_pos, normalized_pos, shift_held, alt_held)  # Handle other clicks
            else:  # If in navigation mode
                if pygame.mouse.get_pressed()[0]:  # Left click
                    clicked_node = self.map_editor._find_node_at_position(normalized_pos)  # Find the clicked node
                    if clicked_node and not self.map_editor.campus_data.locations[clicked_node].is_waypoint:  # If a valid node is clicked
                        self.nav_handler.handle_node_click(clicked_node)  # Handle node click for navigation
                        print(f"Selected node: {clicked_node}")  # Print the selected node

    def _update_display(self):
        """Update the display by drawing the map and UI elements."""
        # Clear screen and draw map
        self.map_handler.screen.fill((255, 255, 255))  # Fill the screen with white
        self.map_handler.draw_map()  # Draw the map

        # Draw edges
        for path in self.map_editor.campus_data.paths:  # Loop through all paths
            start_loc = self.map_editor.campus_data.locations[path.start_id]  # Get the start location
            end_loc = self.map_editor.campus_data.locations[path.end_id]  # Get the end location
            start_pos = (
                int(start_loc.x * self.map_handler.map_width) + self.map_handler.console_width,  # Calculate start position
                int(start_loc.y * self.map_handler.window_height)  # Calculate start position
            )
            end_pos = (
                int(end_loc.x * self.map_handler.map_width) + self.map_handler.console_width,  # Calculate end position
                int(end_loc.y * self.map_handler.window_height)  # Calculate end position
            )
            
            # Draw path with different color if it's part of the current route
            if not self.edit_mode and self.nav_handler.nav_state.current_path:  # If not in edit mode and there is a current path
                path_nodes = self.nav_handler.nav_state.current_path['nodes']  # Get the nodes in the current path
                if (path.start_id in path_nodes and path.end_id in path_nodes and 
                    abs(path_nodes.index(path.start_id) - path_nodes.index(path.end_id)) == 1):  # Check if the path is part of the route
                    # Path is part of the route
                    color = self.nav_handler.nav_state.path_colors[self.nav_handler.nav_state.path_type]  # Get the color for the path
                    pygame.draw.line(self.map_handler.screen, color, start_pos, end_pos, 4)  # Draw the path
                else:
                    # Regular path
                    pygame.draw.line(self.map_handler.screen, (180, 180, 180), start_pos, end_pos, 2)  # Draw regular path
            else:
                # Regular path in edit mode
                pygame.draw.line(self.map_handler.screen, (180, 180, 180), start_pos, end_pos, 2)  # Draw regular path

        # Draw nodes
        for loc_id, location in self.map_editor.campus_data.locations.items():  # Loop through all locations
            pos = (
                int(location.x * self.map_handler.map_width) + self.map_handler.console_width,  # Calculate node position
                int(location.y * self.map_handler.window_height)  # Calculate node position
            )
            
            if location.is_waypoint:  # If the location is a waypoint
                # Smaller gray circles for waypoints
                pygame.draw.circle(self.map_handler.screen, (200, 200, 200), pos, 4)  # Draw waypoint
            else:
                # Different colors for selected nodes in navigation mode
                if not self.edit_mode:  # If not in edit mode
                    if loc_id == self.nav_handler.nav_state.start_node:  # If the node is the start node
                        color = self.nav_handler.nav_state.path_colors['selected']  # Get selected color
                    elif loc_id == self.nav_handler.nav_state.end_node:  # If the node is the end node
                        color = self.nav_handler.nav_state.path_colors['selected']  # Get selected color
                    else:
                        color = (50, 100, 150)  # Default node color
                else:
                    color = (50, 100, 150)  # Default node color
                    
                pygame.draw.circle(self.map_handler.screen, (255, 255, 255), pos, 8)  # Draw outer circle
                pygame.draw.circle(self.map_handler.screen, color, pos, 6)  # Draw inner circle

        # Draw UI elements
        self.console_panel.draw()  # Draw the console panel
        if self.text_input.active:  # If text input is active
            self.text_input.draw()  # Draw the text input field

        pygame.display.flip()  # Update the display

if __name__ == "__main__":
    navigator = CSUFNavigator()  # Create an instance of CSUFNavigator
    navigator.run()  # Run the navigator

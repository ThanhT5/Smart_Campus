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
        
        # Don't initialize navigation yet
        self.graph_manager = None  # Placeholder for the graph manager
        self.nav_handler = None  # Placeholder for the navigation handler
        
        # Load map and initialize navigation
        if self.map_editor.load_map():  # Load map immediately
            self.initialize_navigation()  # Initialize only after loading
            self.console_panel.nav_handler = self.nav_handler  # Link the navigation handler to the console panel
        
        self.edit_mode = True  # Set the initial mode to edit mode
        self.running = True  # Set the running state to true

    def initialize_navigation(self):
        """Initialize or reinitialize the navigation system"""
        print("\nInitializing navigation system...")  # Log initialization
        self.graph_manager = GraphManager(self.map_editor.campus_data)  # Create a graph manager with campus data
        self.nav_handler = NavigationHandler(self.graph_manager, self.console_panel)  # Create a navigation handler
        print(f"Graph initialized with {self.graph_manager.G.number_of_nodes()} nodes and {self.graph_manager.G.number_of_edges()} edges")  # Log graph details

    def handle_map_load(self):
        """Handle map loading and reinitialize navigation"""
        if self.map_editor.load_map():  # Attempt to load the map
            print("\nReinitializing navigation after map load...")  # Log reinitialization
            self.initialize_navigation()  # Reinitialize with loaded data
            print(f"Navigation reinitialized with {self.graph_manager.G.number_of_nodes()} nodes")  # Log reinitialization details
            return True  # Indicate successful load
        return False  # Indicate failure to load

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
                    # Add this before other click handling
                    if not self.edit_mode:  # If not in edit mode
                        # Check if clicked on console panel dropdown
                        console_click = self.console_panel.handle_click(event.pos)  # Handle console panel click
                        if console_click:  # If dropdown was clicked
                            continue  # Skip other click handling
                    
                    self._handle_mouse_click(event)  # Handle mouse click events
            elif event.type == pygame.MOUSEMOTION:  # Check for mouse motion events
                self.mouse_pos = event.pos  # Update mouse position
            elif event.type == pygame.KEYDOWN:  # Check for key presses again
                # Handle Ctrl+L for loading
                if event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:  # If Ctrl + L is pressed
                    self.handle_map_load()  # Load the map

    def _handle_keypress(self, key):
        """Handle key presses for various commands."""
        if self.edit_mode:  # If in edit mode
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
            elif key == pygame.K_m:  # If the M key is pressed
                self.map_handler.toggle_map()  # Toggle the map display
            elif key == pygame.K_a:  # If the A key is pressed
                self.map_editor.is_accessible = not self.map_editor.is_accessible  # Toggle accessibility mode
                print(f"Accessibility mode: {'ON' if self.map_editor.is_accessible else 'OFF'}")  # Print current accessibility status
        else:  # If not in edit mode
            if key == pygame.K_ESCAPE:  # If the Escape key is pressed
                self.running = False  # Stop the main loop
            elif key == pygame.K_r:  # If the R key is pressed
                self.nav_handler.reset_selection()  # Reset the current selection
            elif key == pygame.K_e:  # If the E key is pressed
                self.edit_mode = not self.edit_mode  # Toggle edit mode
                self.map_editor.edit_mode = self.edit_mode  # Update the map editor's edit mode
            elif key == pygame.K_a:  # If the A key is pressed
                self.nav_handler.accessibility = not self.nav_handler.accessibility  # Toggle accessibility mode
                print(f"Accessibility mode: {'ON' if self.nav_handler.accessibility else 'OFF'}")  # Print current accessibility status

    def _handle_mouse_click(self, event):
        """Handle mouse click events for node and edge creation."""
        map_pos = self.map_handler.screen_to_map_coords(event.pos)  # Convert screen position to map coordinates
        
        if map_pos[0] >= 0 and map_pos[0] <= self.map_handler.map_width:  # Check if the click is within map bounds
            normalized_pos = self.map_handler.map_to_normalized_coords(map_pos)  # Normalize the map position
            
            if self.edit_mode:  # If in edit mode
                # Existing edit mode code
                if self.map_editor.is_accessible:  # Using map_editor's flag
                    # Handle path accessibility toggling
                    clicked_path = self.map_handler.get_clicked_path(event.pos, self.graph_manager)  # Get the clicked path
                    if clicked_path:  # If a path was clicked
                        self._toggle_path_accessibility(clicked_path)  # Toggle accessibility for the path
                else:  # If not in accessibility editing mode
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
                        # Check if we already have both nodes selected
                        if self.nav_handler.nav_state.start_node and self.nav_handler.nav_state.end_node:
                            print("2 nodes already selected. Press 'R' to reset selection.")  # Inform user about selection
                        else:
                            self.nav_handler.handle_node_click(clicked_node)  # Handle node click for navigation
                            print(f"Selected node: {clicked_node}")  # Print the selected node

    def _update_display(self):
        """Update the display with current state."""
        self.map_handler.screen.fill((0, 0, 0))  # Fill with black background
        self.map_handler.draw_map()  # Draw the map
        
        # Draw edges
        for path in self.map_editor.campus_data.paths:  # Iterate through all paths
            start_loc = self.map_editor.campus_data.locations[path.start_id]  # Get start location
            end_loc = self.map_editor.campus_data.locations[path.end_id]  # Get end location
            start_pos = (
                int(start_loc.x * self.map_handler.map_width) + self.map_handler.console_width,  # Calculate start position
                int(start_loc.y * self.map_handler.window_height)  # Calculate start position
            )
            end_pos = (
                int(end_loc.x * self.map_handler.map_width) + self.map_handler.console_width,  # Calculate end position
                int(end_loc.y * self.map_handler.window_height)  # Calculate end position
            )
            
            # Draw path with different color based on mode and accessibility
            if self.edit_mode and self.map_editor.is_accessible:  # In accessibility editing mode
                # Show green for accessible paths
                color = (0, 255, 0) if path.is_accessible else (255, 255, 0)  # Green if accessible, yellow otherwise
                pygame.draw.line(self.map_handler.screen, color, start_pos, end_pos, 2)  # Draw the path
            elif not self.edit_mode and self.nav_handler.nav_state.current_path:  # In navigation mode with a current path
                path_nodes = self.nav_handler.nav_state.current_path['nodes']  # Get current path nodes
                if (path.start_id in path_nodes and path.end_id in path_nodes and 
                    abs(path_nodes.index(path.start_id) - path_nodes.index(path.end_id)) == 1):  # Check if path is part of the route
                    # Path is part of the route - draw in red
                    pygame.draw.line(self.map_handler.screen, (255, 0, 0), start_pos, end_pos, 4)  # Draw the path in red
                else:
                    # Regular path - draw in yellow
                    pygame.draw.line(self.map_handler.screen, (255, 255, 0), start_pos, end_pos, 2)  # Draw the path in yellow
            else:
                # Regular path - draw in yellow
                pygame.draw.line(self.map_handler.screen, (255, 255, 0), start_pos, end_pos, 2)  # Draw the path in yellow

        # Draw nodes
        for loc_id, location in self.map_editor.campus_data.locations.items():  # Iterate through all locations
            pos = (
                int(location.x * self.map_handler.map_width) + self.map_handler.console_width,  # Calculate position
                int(location.y * self.map_handler.window_height)  # Calculate position
            )
            
            if location.is_waypoint:  # If the location is a waypoint
                # Draw waypoints in yellow
                pygame.draw.circle(self.map_handler.screen, (255, 255, 0), pos, 4)  # Draw waypoint
            else:  # If not a waypoint
                # Different colors for selected nodes in navigation mode
                if not self.edit_mode:  # If not in edit mode
                    if loc_id == self.nav_handler.nav_state.start_node:  # If this is the start node
                        color = self.nav_handler.nav_state.path_colors['selected']  # Get selected color
                    elif loc_id == self.nav_handler.nav_state.end_node:  # If this is the end node
                        color = self.nav_handler.nav_state.path_colors['selected']  # Get selected color
                    else:
                        color = (50, 100, 150)  # Default color for other nodes
                else:
                    color = (50, 100, 150)  # Default color for edit mode
                    
                pygame.draw.circle(self.map_handler.screen, (255, 255, 255), pos, 8)  # Draw white outline
                pygame.draw.circle(self.map_handler.screen, color, pos, 6)  # Draw colored center

        # Draw UI elements
        self.console_panel.draw()  # Draw the console panel
        if self.text_input.active:  # If text input is active
            self.text_input.draw()  # Draw the text input field

        pygame.display.flip()  # Update the display

    def _draw(self):
        """Draw the application window"""
        self.screen.fill(255, 255, 255)  # Fill the screen with white
        
        # Draw map with current path if it exists
        current_path = None  # Initialize current path
        if self.nav_handler.nav_state.current_path:  # If there is a current path
            current_path = self.nav_handler.nav_state.current_path['nodes']  # Get current path nodes
        
        self.map_handler.draw_graph(self.graph_manager, current_path)  # Draw the graph with current path
        self.console_panel.draw()  # Draw the console panel
        
        pygame.display.flip()  # Update the display

    def _toggle_path_accessibility(self, path_ids: tuple):
        """Toggle accessibility for a path"""
        start_id, end_id = path_ids  # Unpack path IDs
        for path in self.map_editor.campus_data.paths:  # Iterate through all paths
            if ((path.start_id == start_id and path.end_id == end_id) or
                (path.start_id == end_id and path.end_id == start_id)):  # Check if path matches
                path.is_accessible = not path.is_accessible  # Toggle accessibility
                print(f"Toggled accessibility for path {start_id} -> {end_id}: {path.is_accessible}")  # Log accessibility change
                break  # Exit loop after toggling

if __name__ == "__main__":
    navigator = CSUFNavigator()  # Create an instance of CSUFNavigator
    navigator.run()  # Run the navigator

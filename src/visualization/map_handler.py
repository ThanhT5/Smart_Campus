import pygame  # Import the pygame library for graphics and game development
import pygame.font  # Import the font module from pygame for text rendering
from typing import Tuple, Optional  # Import Tuple and Optional for type hinting
from core.graph_manager import GraphManager  # Import GraphManager for handling graph-related operations

class MapHandler:
    """Handles the display and interaction with the campus map."""
    
    def __init__(self):
        pygame.init()  # Ensure Pygame is initialized
        
        # Define layout dimensions
        self.console_width = 200  # Width of console panel
        self.map_width = 800      # Width of map area
        self.window_height = 600  # Total window height
        
        # Total window size includes console and map
        self.window_size = (self.console_width + self.map_width, self.window_height)
        self.map_rect = pygame.Rect(self.console_width, 0, self.map_width, self.window_height)  # Define the map area rectangle
        
        self.screen = pygame.display.set_mode(self.window_size)  # Set the display mode with the defined window size
        pygame.display.set_caption("CSUF Navigator")  # Set the window title
        
        # Load multiple background images (scale to map area, not full window)
        self.background_maps = {
            'default': self._load_and_scale_image('assets/campus_map.png'),  # Load default campus map
            'bike': self._load_and_scale_image('assets/bike_paths.png'),  # Load bike paths map
            'walking': self._load_and_scale_image('assets/walking_paths.png'),  # Load walking paths map
            # Add more maps as needed
        }
        
        # Current active map
        self.current_map = 'default'  # Set the initial active map to default
        
        # Initialize font
        self.font = pygame.font.Font(None, 24)  # Create a font object for rendering text
        
        # Debug mode and selection state
        self.debug_mode = False  # Flag for enabling debug mode
        self.selected_start = None  # Variable to store the selected start location
        self.selected_end = None  # Variable to store the selected end location
        self.current_path = []  # List to store the current path
        
        print("MapHandler initialized with window size:", self.window_size)  # Debug print to confirm initialization
        
        # Colors
        self.node_color = (50, 100, 150)  # Color for nodes
        self.edge_color = (180, 180, 180)  # Color for edges
        self.path_color = (255, 100, 100)  # Color for paths
        self.text_color = (50, 50, 50)  # Color for text
        
        # Display settings
        self.node_radius = 6  # Radius for nodes
        self.selected_node_radius = 10  # Radius for selected nodes
    
    def _load_and_scale_image(self, path: str) -> pygame.Surface:
        """Load and scale an image to map area size (not full window)."""
        try:
            img = pygame.image.load(path)  # Load the image from the specified path
            return pygame.transform.scale(img, (self.map_width, self.window_height))  # Scale the image to fit the map area
        except (pygame.error, FileNotFoundError):  # Handle errors if the image cannot be loaded
            surface = pygame.Surface((self.map_width, self.window_height))  # Create a blank surface
            surface.fill((255, 255, 255))  # Fill the surface with white color
            return surface  # Return the blank surface

    def toggle_map(self):
        """Toggle between different map types."""
        map_types = list(self.background_maps.keys())  # Get the list of available map types
        current_index = map_types.index(self.current_map)  # Find the index of the current map
        next_index = (current_index + 1) % len(map_types)  # Calculate the index of the next map
        self.current_map = map_types[next_index]  # Update the current map to the next one
        print(f"Switched to {self.current_map} map")  # Print the current map for debugging

    def draw_map(self):
        """Draw the current background map."""
        # Draw the current background map
        if self.current_map in self.background_maps:  # Check if the current map is valid
            self.screen.blit(
                self.background_maps[self.current_map],  # Draw the current map
                (self.console_width, 0)  # Position after console panel
            )

    # def draw_map_indicator(self):
    #     """Draw current map type indicator."""
    #     text = self.font.render(f"Current Map: {self.current_map}", True, self.text_color)  # Render the current map text
    #     text_rect = text.get_rect(topleft=(10, self.window_size[1] - 30))  # Get the rectangle for positioning the text
    #     # Draw text background
    #     pygame.draw.rect(self.screen, (255, 255, 255, 180), text_rect.inflate(20, 10))  # Draw a background rectangle for the text
    #     self.screen.blit(text, text_rect)  # Draw the text on the screen
    
    def _transform_coordinates(self, x: float, y: float) -> Tuple[int, int]:
        """
        Transform normalized coordinates (0-1) to screen coordinates.
        
        Args:
            x: Normalized x coordinate (0-1)
            y: Normalized y coordinate (0-1)
            
        Returns:
            Tuple of screen coordinates (x, y)
        """
        usable_width = self.window_size[0] - 2 * self.margin  # Calculate usable width considering margins
        usable_height = self.window_size[1] - 2 * self.margin  # Calculate usable height considering margins
        
        screen_x = self.margin + (x * usable_width)  # Calculate the screen x coordinate
        screen_y = self.margin + (y * usable_height)  # Calculate the screen y coordinate
        
        return (int(screen_x), int(screen_y))  # Return the screen coordinates as integers
    
    def _inverse_transform_coordinates(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """
        Transform screen coordinates back to normalized coordinates (0-1).
        
        Args:
            screen_x: Screen x coordinate
            screen_y: Screen y coordinate
            
        Returns:
            Tuple of normalized coordinates (x, y)
        """
        usable_width = self.window_size[0] - 2 * self.margin  # Calculate usable width considering margins
        usable_height = self.window_size[1] - 2 * self.margin  # Calculate usable height considering margins
        
        x = (screen_x - self.margin) / usable_width  # Calculate normalized x coordinate
        y = (screen_y - self.margin) / usable_height  # Calculate normalized y coordinate
        
        return (x, y)  # Return the normalized coordinates
    
    def handle_click(self, pos: Tuple[int, int], graph_manager: GraphManager) -> Optional[str]:
        """
        Handle mouse clicks for location selection.
        
        Args:
            pos: Mouse click position (x, y)
            graph_manager: GraphManager instance
            
        Returns:
            Location ID if a node was clicked, None otherwise
        """
        for loc_id, location in graph_manager.campus_data.locations.items():  # Iterate through all locations
            node_pos = self._transform_coordinates(location.x, location.y)  # Transform location coordinates to screen coordinates
            distance = ((pos[0] - node_pos[0]) ** 2 + (pos[1] - node_pos[1]) ** 2) ** 0.5  # Calculate the distance from the click position
            
            if distance <= self.node_radius:  # Check if the click is within the node radius
                return loc_id  # Return the location ID if clicked
        return None  # Return None if no node was clicked
    
    # def draw_debug_grid(self):
    #     """Draw coordinate grid and labels for debugging."""
    #     # Draw grid lines
    #     for i in range(11):  # Loop to create 11 grid lines
    #         x = i * (self.window_size[0] - 2 * self.margin) / 10 + self.margin  # Calculate x position for grid line
    #         y = i * (self.window_size[1] - 2 * self.margin) / 10 + self.margin  # Calculate y position for grid line
            
    #         # Grid lines
    #         pygame.draw.line(self.screen, self.grid_color,  # Draw vertical grid line
    #                        (x, self.margin), 
    #                        (x, self.window_size[1] - self.margin), 1)
    #         pygame.draw.line(self.screen, self.grid_color,  # Draw horizontal grid line
    #                        (self.margin, y), 
    #                        (self.window_size[0] - self.margin, y), 1)
            
    #         # Coordinate labels
    #         if i < 10:  # Only draw labels for the first 10 grid lines
    #             text = self.font.render(f"{i/10:.1f}", True, self.text_color)  # Render the label text
    #             self.screen.blit(text, (x - 10, self.margin - 20))  # X-axis labels
    #             self.screen.blit(text, (self.margin - 30, y - 10))  # Y-axis labels
    
    def draw_graph(self, graph_manager: GraphManager) -> None:
        """Draw the graph with nodes and edges."""
        # Draw edges first (so they appear under nodes)
        for edge in graph_manager.graph.edges():  # Iterate through all edges in the graph
            start_loc = graph_manager.campus_data.get_location(edge[0])  # Get the start location of the edge
            end_loc = graph_manager.campus_data.get_location(edge[1])  # Get the end location of the edge
            
            if start_loc and end_loc:  # Check if both locations are valid
                start_pos = self._transform_coordinates(start_loc.x, start_loc.y)  # Transform start location to screen coordinates
                end_pos = self._transform_coordinates(end_loc.x, end_loc.y)  # Transform end location to screen coordinates
                pygame.draw.line(self.screen, (100, 100, 100), start_pos, end_pos, 2)  # Draw the edge line
        
        # Draw nodes
        for node_id in graph_manager.graph.nodes():  # Iterate through all nodes in the graph
            location = graph_manager.campus_data.get_location(node_id)  # Get the location of the node
            if location:  # Check if the location is valid
                pos = self._transform_coordinates(location.x, location.y)  # Transform location to screen coordinates
                # Draw larger node circle
                pygame.draw.circle(self.screen, (0, 0, 255), pos, 10)  # Draw the node as a blue circle
                
                # Draw location name
                text = self.font.render(location.name, True, (0, 0, 0))  # Render the location name
                text_rect = text.get_rect(center=(pos[0], pos[1] - 20))  # Get the rectangle for positioning the text
                self.screen.blit(text, text_rect)  # Draw the location name on the screen

    def screen_to_map_coords(self, screen_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert screen coordinates to map coordinates."""
        return (screen_pos[0] - self.console_width, screen_pos[1])  # Adjust x coordinate by console width

    def map_to_normalized_coords(self, map_pos: Tuple[int, int]) -> Tuple[float, float]:
        """Convert map coordinates to normalized coordinates (0-1)."""
        return (
            map_pos[0] / self.map_width,  # Normalize x coordinate
            map_pos[1] / self.window_height  # Normalize y coordinate
        )

    def draw_path(self, path: list, color: tuple = (255, 0, 0), width: int = 4):
        """Draw the selected path with thicker lines"""
        if not path:
            return
            
        for i in range(len(path['nodes']) - 1):
            start_id = path['nodes'][i]
            end_id = path['nodes'][i + 1]
            
            start_loc = self.graph_manager.campus_data.locations[start_id]
            end_loc = self.graph_manager.campus_data.locations[end_id]
            
            start_pos = self._transform_coordinates(start_loc.x, start_loc.y)
            end_pos = self._transform_coordinates(end_loc.x, end_loc.y)
            
            pygame.draw.line(self.screen, color, start_pos, end_pos, width)

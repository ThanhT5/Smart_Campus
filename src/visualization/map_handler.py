import pygame  # Import the pygame library for graphics and game development
import pygame.font  # Import the font module from pygame for text rendering
from typing import Tuple, Optional, List  # Import Tuple, Optional, and List for type hinting
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
        
        self.path_click_threshold = 5  # Pixels distance for path click detection
    
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
    
    def draw_graph(self, graph_manager: GraphManager, current_path: Optional[List[str]] = None) -> None:
        """Draw the graph with optional path highlighting"""
        # Draw all edges first
        for edge in graph_manager.get_edge_list():
            start_loc = graph_manager.campus_data.locations[edge[0]]  # Get starting location for the edge
            end_loc = graph_manager.campus_data.locations[edge[1]]  # Get ending location for the edge
            
            start_pos = (
                int(start_loc.x * self.map_width) + self.console_width,  # Calculate starting position on the screen
                int(start_loc.y * self.window_height)  # Calculate starting position on the screen
            )
            end_pos = (
                int(end_loc.x * self.map_width) + self.console_width,  # Calculate ending position on the screen
                int(end_loc.y * self.window_height)  # Calculate ending position on the screen
            )
            
            # Get path object to check accessibility
            path = next((p for p in graph_manager.campus_data.paths 
                        if (p.start_id == edge[0] and p.end_id == edge[1]) or 
                           (p.start_id == edge[1] and p.end_id == edge[0])), None)  # Find the path object
            
            if path:
                # Color based on accessibility
                color = (0, 255, 0) if path.is_accessible else (255, 255, 0)  # Green if accessible, yellow otherwise
                pygame.draw.line(self.screen, color, start_pos, end_pos, 2)  # Draw the edge with the determined color
        
        # Draw nodes last (on top of edges)
        for loc_id, location in graph_manager.campus_data.locations.items():  # Iterate through all locations
            pos = (
                int(location.x * self.map_width) + self.console_width,  # Calculate position on the screen
                int(location.y * self.window_height)  # Calculate position on the screen
            )
            
            if location.is_waypoint:
                # Draw waypoints in yellow
                pygame.draw.circle(self.screen, (255, 255, 0), pos, 4)  # Draw waypoint
            else:
                # Draw regular nodes
                pygame.draw.circle(self.screen, (255, 255, 255), pos, 8)  # Draw white outline for regular nodes
                pygame.draw.circle(self.screen, (50, 100, 150), pos, 6)   # Draw blue center for regular nodes

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
        if not path:  # Check if the path is empty
            return  # Exit if no path to draw
            
        for i in range(len(path['nodes']) - 1):  # Iterate through nodes in the path
            start_id = path['nodes'][i]  # Get starting node ID
            end_id = path['nodes'][i + 1]  # Get ending node ID
            
            start_loc = self.graph_manager.campus_data.locations[start_id]  # Get starting location
            end_loc = self.graph_manager.campus_data.locations[end_id]  # Get ending location
            
            start_pos = self._transform_coordinates(start_loc.x, start_loc.y)  # Transform starting location to screen coordinates
            end_pos = self._transform_coordinates(end_loc.x, end_loc.y)  # Transform ending location to screen coordinates
            
            pygame.draw.line(self.screen, color, start_pos, end_pos, width)  # Draw the path segment

    def get_clicked_path(self, click_pos: Tuple[int, int], graph_manager: GraphManager) -> Optional[Tuple[str, str]]:
        """Detect if a path was clicked"""
        def point_to_line_distance(point, line_start, line_end):
            """Calculate distance from point to line segment"""
            px, py = point  # Unpack point coordinates
            x1, y1 = line_start  # Unpack line start coordinates
            x2, y2 = line_end  # Unpack line end coordinates
            
            # Calculate the length of the line segment
            line_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            if line_length == 0:  # If the line length is zero
                return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5  # Return distance to the start point
            
            # Calculate the distance from point to line
            t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_length ** 2)))  # Project point onto line
            proj_x = x1 + t * (x2 - x1)  # Calculate projected x coordinate
            proj_y = y1 + t * (y2 - y1)  # Calculate projected y coordinate
            return ((px - proj_x) ** 2 + (py - proj_y) ** 2) ** 0.5  # Return distance to the line

        # Check each path
        for path in graph_manager.campus_data.paths:  # Iterate through all paths
            start_loc = graph_manager.campus_data.locations[path.start_id]  # Get starting location for the path
            end_loc = graph_manager.campus_data.locations[path.end_id]  # Get ending location for the path
            
            start_pos = (
                int(start_loc.x * self.map_width) + self.console_width,  # Calculate starting position on the screen
                int(start_loc.y * self.window_height)  # Calculate starting position on the screen
            )
            end_pos = (
                int(end_loc.x * self.map_width) + self.console_width,  # Calculate ending position on the screen
                int(end_loc.y * self.window_height)  # Calculate ending position on the screen
            )
            
            # Check if click is near this path
            distance = point_to_line_distance(click_pos, start_pos, end_pos)  # Calculate distance from click to path
            if distance <= self.path_click_threshold:  # Check if distance is within threshold
                return (path.start_id, path.end_id)  # Return the IDs of the clicked path
        
        return None  # Return None if no path was clicked

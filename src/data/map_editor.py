import pygame  # Import the pygame library for graphics and game development

from pathlib import Path as PathLib  # Import Path for handling file paths
from typing import Tuple, Optional  # Import Tuple and Optional for type hinting
from .campus_data import Location, Path, CampusData  # Import necessary classes from campus_data module

class MapEditor:
    def __init__(self):
        # Initialize the MapEditor with campus data and default values
        self.campus_data = CampusData()  # Create an instance of CampusData to manage locations and paths
        self.selected_node = None  # Variable to store the currently selected node
        self.drawing_edge = False  # Flag to indicate if an edge is currently being drawn
        self.edge_start = None  # Variable to store the starting node of the edge being drawn
        self.is_accessible = False  # Flag to indicate if the edge is accessible
        self.delete_mode = False  # Flag to indicate if delete mode is active
        self.edge_click_threshold = 0.02  # Threshold for edge detection (distance)
        self.pending_node = None  # Variable to store information about a node being created
        self.scale_factor = 750  # Scale factor for converting normalized coordinates to meters
        self.edit_mode = True  # Flag to indicate if the editor is in edit mode

    def handle_click(self, pos: Tuple[int, int], normalized_pos: Tuple[float, float], shift_held: bool, alt_held: bool) -> None:
        """Handle mouse clicks for node/edge creation/deletion"""
        clicked_node = self._find_node_at_position(normalized_pos)  # Find if a node was clicked at the normalized position

        if shift_held:  # Check if the shift key is held for delete mode
            if pygame.mouse.get_pressed()[2]:  # Check for right mouse button click
                if clicked_node:  # If a node was clicked
                    self._remove_node(clicked_node)  # Remove the clicked node
                    print(f"Removed node: {clicked_node}")  # Debug message for node removal
                    self._reset_edge_drawing()  # Reset edge drawing state
                else:
                    # Check if clicked on an edge
                    clicked_edge = self._find_edge_at_position(normalized_pos)  # Find if an edge was clicked
                    if clicked_edge:  # If an edge was clicked
                        self._remove_edge(clicked_edge)  # Remove the clicked edge
                        print(f"Removed edge between {clicked_edge[0]} and {clicked_edge[1]}")  # Debug message for edge removal
        else:  # Normal mode
            if pygame.mouse.get_pressed()[0]:  # Check for left mouse button click
                if not self.drawing_edge:  # If not currently drawing an edge
                    if alt_held:  # Check if the alt key is held
                        # Create waypoint directly without name input
                        self._create_waypoint(normalized_pos)  # Create a waypoint at the clicked position
                    else:
                        # Create building node (will trigger name input)
                        self._handle_node_creation(normalized_pos)  # Handle creation of a new building node
            
            elif pygame.mouse.get_pressed()[2]:  # Check for right mouse button click
                self._handle_edge_creation(clicked_node)  # Handle edge creation logic

    def _create_waypoint(self, normalized_pos: Tuple[float, float]) -> None:
        """Create an unnamed waypoint node"""
        # Find the next available waypoint number
        existing_waypoints = [int(loc_id.split('_')[1]) for loc_id in self.campus_data.locations.keys() 
                             if loc_id.startswith('waypoint_')]  # List existing waypoints
        next_number = max(existing_waypoints, default=-1) + 1  # Determine the next waypoint number
        
        node_id = f"waypoint_{next_number}"  # Create a unique ID for the new waypoint
        new_location = Location(
            id=node_id,  # Set the ID for the new location
            name="",  # Empty name for waypoints
            x=normalized_pos[0],  # Set x coordinate
            y=normalized_pos[1],  # Set y coordinate
            type="waypoint",  # Specify the type as waypoint
            is_waypoint=True,  # Set the is_waypoint flag to True
            is_accessible=self.is_accessible  # Set accessibility based on the current state
        )
        self.campus_data.add_location(new_location)  # Add the new location to campus data
        print(f"Created waypoint: {node_id}")  # Debug message for waypoint creation

    def _handle_node_creation(self, normalized_pos: Tuple[float, float], screen_pos: Tuple[int, int]) -> None:
        """Handle creation of new building nodes"""
        node_id = f"node_{len(self.campus_data.locations)}"  # Create a unique ID for the new node
        self.pending_node = {
            'id': node_id,  # Store the ID of the pending node
            'pos': normalized_pos,  # Store the normalized position of the pending node
            'screen_pos': screen_pos,  # Store the screen position of the pending node
            'type': 'building'  # Specify this is a building node
        }

    def complete_node_creation(self, name: str, full_name: str = None) -> None:
        """Complete building node creation with provided name"""
        if self.pending_node:  # Check if there is a pending node to complete
            new_location = Location(
                id=self.pending_node['id'],  # Set the ID for the new location
                name=name,  # Set the name for the new location
                full_name=full_name or name,  # Set the full name, defaulting to name if not provided
                x=self.pending_node['pos'][0],  # Set x coordinate from pending node
                y=self.pending_node['pos'][1],  # Set y coordinate from pending node
                type=self.pending_node['type'],  # Set the type from pending node
                is_waypoint=False  # Set is_waypoint flag to False
            )
            self.campus_data.add_location(new_location)  # Add the new location to campus data
            print(f"Created building node: {name} ({self.pending_node['id']})")  # Debug message for building node creation
            self.pending_node = None  # Reset pending node after creation

    def _handle_edge_creation(self, clicked_node: Optional[str]) -> None:
        """Handle edge creation logic"""
        if not self.drawing_edge:  # Check if not currently drawing an edge
            if clicked_node:  # If a node was clicked
                # Start drawing edge from clicked node
                self.edge_start = clicked_node  # Set the starting node for the edge
                self.drawing_edge = True  # Set the drawing edge flag to True
                print(f"Starting edge from: {clicked_node}")  # Debug message for starting edge
        else:
            if clicked_node:  # If a node was clicked while drawing an edge
                # Trying to complete edge
                if clicked_node == self.edge_start:  # Check if clicked the same node
                    print("Cannot create edge to same node")  # Debug message for invalid edge creation
                    self._reset_edge_drawing()  # Reset edge drawing state
                elif self._edge_exists(self.edge_start, clicked_node):  # Check if edge already exists
                    print("Edge already exists")  # Debug message for existing edge
                    self._reset_edge_drawing()  # Reset edge drawing state
                else:
                    self._create_edge(self.edge_start, clicked_node)  # Create the edge
                    print(f"Created edge: {self.edge_start} -> {clicked_node}")  # Debug message for edge creation
                    self._reset_edge_drawing()  # Reset edge drawing state
            else:
                # Clicked empty space, cancel edge creation
                print("Edge creation cancelled")  # Debug message for cancelled edge creation
                self._reset_edge_drawing()  # Reset edge drawing state

    def _reset_edge_drawing(self) -> None:
        """Reset edge drawing state"""
        self.drawing_edge = False  # Set drawing edge flag to False
        self.edge_start = None  # Clear the starting node for edge drawing

    def _edge_exists(self, start_id: str, end_id: str) -> bool:
        """Check if an edge already exists between two nodes"""
        for path in self.campus_data.paths:  # Iterate through existing paths
            if (path.start_id == start_id and path.end_id == end_id) or \
               (path.start_id == end_id and path.end_id == start_id):  # Check for both directions
                return True  # Return True if edge exists
        return False  # Return False if edge does not exist

    def _calculate_distance(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float]) -> float:
        """Calculate the Euclidean distance between two points and convert to meters"""
        dx = (end_pos[0] - start_pos[0]) * self.scale_factor  # Calculate x distance
        dy = (end_pos[1] - start_pos[1]) * self.scale_factor  # Calculate y distance
        # Convert normalized coordinates to approximate real-world meters
        # Assuming the map represents roughly a 1km x 1km area
        return round(((dx ** 2 + dy ** 2) ** 0.5), 1)  # Round to 1 decimal place

    def _create_edge(self, start_id: str, end_id: str) -> None:
        """Create a new edge between two nodes with calculated distance"""
        if start_id and end_id and start_id != end_id:  # Ensure valid edge creation
            start_loc = self.campus_data.locations[start_id]  # Get starting location
            end_loc = self.campus_data.locations[end_id]  # Get ending location
            
            # Calculate distance
            distance = self._calculate_distance(
                (start_loc.x, start_loc.y),  # Starting coordinates
                (end_loc.x, end_loc.y)  # Ending coordinates
            )
            
            # Create the path
            new_path = Path(
                start_id=start_id,  # Set starting ID
                end_id=end_id,  # Set ending ID
                distance=distance,  # Set calculated distance
                path_type="walkway",  # Specify path type
                is_accessible=self.is_accessible  # Set accessibility based on current state
            )
            self.campus_data.add_path(new_path)  # Add the new path to campus data
            
            # Update connections in both locations
            if end_id not in start_loc.connections:  # Check if connection does not exist
                start_loc.connections.append(end_id)  # Add connection to start location
            if start_id not in end_loc.connections:  # Check if connection does not exist
                end_loc.connections.append(start_id)  # Add connection to end location
            
            print(f"Created edge: {start_id} -> {end_id} (Distance: {distance:.1f}m)")  # Debug message for edge creation

    def _remove_node(self, node_id: str) -> None:
        """Remove a node and all its connected edges"""
        if node_id in self.campus_data.locations:  # Check if the node exists
            # Remove all paths connected to this node
            self.campus_data.paths = [
                path for path in self.campus_data.paths 
                if path.start_id != node_id and path.end_id != node_id  # Filter out paths connected to the node
            ]
            
            # Remove node from other nodes' connections
            for location in self.campus_data.locations.values():  # Iterate through all locations
                if node_id in location.connections:  # Check if the node is in connections
                    location.connections.remove(node_id)  # Remove the node from connections
            
            # Remove the node itself
            del self.campus_data.locations[node_id]  # Delete the node from campus data

    def _find_node_at_position(self, normalized_pos: Tuple[float, float]) -> Optional[str]:
        """Find if there's a node at the given position"""
        for loc_id, location in self.campus_data.locations.items():  # Iterate through all locations
            distance = ((normalized_pos[0] - location.x) ** 2 + 
                       (normalized_pos[1] - location.y) ** 2) ** 0.5  # Calculate distance to the node
            if distance < 0.02:  # Threshold for clicking near a node
                return loc_id  # Return the ID of the clicked node
        return None  # Return None if no node was found

    def get_current_edge_drawing(self) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """Get the coordinates of the edge currently being drawn"""
        if self.drawing_edge and self.edge_start:  # Check if an edge is being drawn
            start_loc = self.campus_data.locations[self.edge_start]  # Get the starting location
            return ((start_loc.x, start_loc.y), None)  # Return the coordinates of the edge start
        return None  # Return None if no edge is being drawn

    def save_map(self) -> None:
        """Save the current map to JSON"""
        data_dir = PathLib(__file__).parent.parent.parent / "data"  # Define the data directory path
        data_dir.mkdir(exist_ok=True)  # Create the directory if it does not exist
        
        self.campus_data.save_to_json(data_dir / "locations.json")  # Save campus data to JSON file
        print("Map saved successfully!")  # Debug message for successful save

    def load_map(self) -> bool:
        """Load map from JSON"""
        data_dir = PathLib(__file__).parent.parent.parent / "data"  # Define the data directory path
        json_path = data_dir / "locations.json"  # Define the path to the JSON file
        
        if json_path.exists():  # Check if the JSON file exists
            self.campus_data = CampusData.load_from_json(json_path)  # Load campus data from JSON file
            print(f"Map loaded with {len(self.campus_data.locations)} locations and {len(self.campus_data.paths)} paths")  # Debug message for loaded map
            return True  # Return True if loading was successful
        return False  # Return False if loading failed

    def _find_edge_at_position(self, pos: Tuple[float, float]) -> Optional[Tuple[str, str]]:
        """Find if there's an edge at the given position"""
        for path in self.campus_data.paths:  # Iterate through all paths
            start_loc = self.campus_data.locations[path.start_id]  # Get starting location
            end_loc = self.campus_data.locations[path.end_id]  # Get ending location
            
            # Calculate distance from point to line segment
            distance = self._point_to_line_distance(
                pos,  # Point to check
                (start_loc.x, start_loc.y),  # Start of the line segment
                (end_loc.x, end_loc.y)  # End of the line segment
            )
            
            if distance < self.edge_click_threshold:  # Check if the distance is within the threshold
                return (path.start_id, path.end_id)  # Return the IDs of the edge
        return None  # Return None if no edge was found

    def _point_to_line_distance(self, point: Tuple[float, float], 
                              line_start: Tuple[float, float], 
                              line_end: Tuple[float, float]) -> float:
        """Calculate the distance from a point to a line segment"""
        x, y = point  # Unpack point coordinates
        x1, y1 = line_start  # Unpack line start coordinates
        x2, y2 = line_end  # Unpack line end coordinates
        
        # Calculate the length of the line segment
        line_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5  # Calculate line length
        
        if line_length == 0:  # Check for degenerate case where line length is zero
            return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5  # Return distance to the start point
            
        # Calculate the distance from point to line
        t = max(0, min(1, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / (line_length ** 2)))  # Project point onto line segment
        
        # Find the nearest point on the line segment
        proj_x = x1 + t * (x2 - x1)  # Calculate projected x coordinate
        proj_y = y1 + t * (y2 - y1)  # Calculate projected y coordinate
        
        # Calculate the distance from the point to the nearest point on the line
        return ((x - proj_x) ** 2 + (y - proj_y) ** 2) ** 0.5  # Return the calculated distance

    def _remove_edge(self, edge: Tuple[str, str]) -> None:
        """Remove an edge and update connections"""
        start_id, end_id = edge  # Unpack edge IDs
        
        # Remove the path
        self.campus_data.paths = [
            path for path in self.campus_data.paths 
            if not ((path.start_id == start_id and path.end_id == end_id) or 
                   (path.start_id == end_id and path.end_id == start_id))  # Filter out the edge to be removed
        ]
        
        # Update connections in both locations
        if start_id in self.campus_data.locations and end_id in self.campus_data.locations:  # Check if both locations exist
            start_loc = self.campus_data.locations[start_id]  # Get starting location
            end_loc = self.campus_data.locations[end_id]  # Get ending location
            
            if end_id in start_loc.connections:  # Check if the end ID is in the start location's connections
                start_loc.connections.remove(end_id)  # Remove the connection
            if start_id in end_loc.connections:  # Check if the start ID is in the end location's connections
                end_loc.connections.remove(start_id)  # Remove the connection
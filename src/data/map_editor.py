import pygame
from pathlib import Path as PathLib
from typing import Tuple, Optional
from .campus_data import Location, Path, CampusData

class MapEditor:
    def __init__(self):
        self.campus_data = CampusData()
        self.selected_node = None
        self.drawing_edge = False
        self.edge_start = None
        self.is_accessible = True
        self.delete_mode = False
        self.edge_click_threshold = 0.02  # Threshold for edge detection
        self.pending_node = None
        self.scale_factor = 750  # Adjust this based on your map scale (meters per unit)
        self.edit_mode = True  # Add edit_mode attribute

    def handle_click(self, pos: Tuple[int, int], normalized_pos: Tuple[float, float], shift_held: bool, alt_held: bool) -> None:
        """Handle mouse clicks for node/edge creation/deletion"""
        clicked_node = self._find_node_at_position(normalized_pos)

        if shift_held:  # Delete mode
            if pygame.mouse.get_pressed()[2]:  # Right click
                if clicked_node:
                    self._remove_node(clicked_node)
                    print(f"Removed node: {clicked_node}")
                    self._reset_edge_drawing()
                else:
                    # Check if clicked on an edge
                    clicked_edge = self._find_edge_at_position(normalized_pos)
                    if clicked_edge:
                        self._remove_edge(clicked_edge)
                        print(f"Removed edge between {clicked_edge[0]} and {clicked_edge[1]}")
        else:  # Normal mode
            if pygame.mouse.get_pressed()[0]:  # Left click
                if not self.drawing_edge:
                    if alt_held:
                        # Create waypoint directly without name input
                        self._create_waypoint(normalized_pos)
                    else:
                        # Create building node (will trigger name input)
                        self._handle_node_creation(normalized_pos)
            
            elif pygame.mouse.get_pressed()[2]:  # Right click
                self._handle_edge_creation(clicked_node)

    def _create_waypoint(self, normalized_pos: Tuple[float, float]) -> None:
        """Create an unnamed waypoint node"""
        # Find the next available waypoint number
        existing_waypoints = [int(loc_id.split('_')[1]) for loc_id in self.campus_data.locations.keys() 
                             if loc_id.startswith('waypoint_')]
        next_number = max(existing_waypoints, default=-1) + 1
        
        node_id = f"waypoint_{next_number}"
        new_location = Location(
            id=node_id,
            name="",  # Empty name for waypoints
            x=normalized_pos[0],
            y=normalized_pos[1],
            type="waypoint",
            is_waypoint=True,
            is_accessible=self.is_accessible
        )
        self.campus_data.add_location(new_location)
        print(f"Created waypoint: {node_id}")

    def _handle_node_creation(self, normalized_pos: Tuple[float, float], screen_pos: Tuple[int, int]) -> None:
        """Handle creation of new building nodes"""
        node_id = f"node_{len(self.campus_data.locations)}"
        self.pending_node = {
            'id': node_id,
            'pos': normalized_pos,
            'screen_pos': screen_pos,
            'type': 'building'  # Specify this is a building node
        }

    def complete_node_creation(self, name: str, full_name: str = None) -> None:
        """Complete building node creation with provided name"""
        if self.pending_node:
            new_location = Location(
                id=self.pending_node['id'],
                name=name,
                full_name=full_name or name,
                x=self.pending_node['pos'][0],
                y=self.pending_node['pos'][1],
                type=self.pending_node['type'],
                is_waypoint=False
            )
            self.campus_data.add_location(new_location)
            print(f"Created building node: {name} ({self.pending_node['id']})")
            self.pending_node = None

    def _handle_edge_creation(self, clicked_node: Optional[str]) -> None:
        """Handle edge creation logic"""
        if not self.drawing_edge:
            if clicked_node:
                # Start drawing edge from clicked node
                self.edge_start = clicked_node
                self.drawing_edge = True
                print(f"Starting edge from: {clicked_node}")
        else:
            if clicked_node:
                # Trying to complete edge
                if clicked_node == self.edge_start:
                    print("Cannot create edge to same node")
                    self._reset_edge_drawing()
                elif self._edge_exists(self.edge_start, clicked_node):
                    print("Edge already exists")
                    self._reset_edge_drawing()
                else:
                    self._create_edge(self.edge_start, clicked_node)
                    print(f"Created edge: {self.edge_start} -> {clicked_node}")
                    self._reset_edge_drawing()
            else:
                # Clicked empty space, cancel edge creation
                print("Edge creation cancelled")
                self._reset_edge_drawing()

    def _reset_edge_drawing(self) -> None:
        """Reset edge drawing state"""
        self.drawing_edge = False
        self.edge_start = None

    def _edge_exists(self, start_id: str, end_id: str) -> bool:
        """Check if an edge already exists between two nodes"""
        for path in self.campus_data.paths:
            if (path.start_id == start_id and path.end_id == end_id) or \
               (path.start_id == end_id and path.end_id == start_id):
                return True
        return False

    def _calculate_distance(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float]) -> float:
        """Calculate the Euclidean distance between two points and convert to meters"""
        dx = (end_pos[0] - start_pos[0]) * self.scale_factor
        dy = (end_pos[1] - start_pos[1]) * self.scale_factor
        # Convert normalized coordinates to approximate real-world meters
        # Assuming the map represents roughly a 1km x 1km area
        return round(((dx ** 2 + dy ** 2) ** 0.5), 1)  # Round to 1 decimal place

    def _create_edge(self, start_id: str, end_id: str) -> None:
        """Create a new edge between two nodes with calculated distance"""
        if start_id and end_id and start_id != end_id:
            start_loc = self.campus_data.locations[start_id]
            end_loc = self.campus_data.locations[end_id]
            
            # Calculate distance
            distance = self._calculate_distance(
                (start_loc.x, start_loc.y),
                (end_loc.x, end_loc.y)
            )
            
            # Create the path
            new_path = Path(
                start_id=start_id,
                end_id=end_id,
                distance=distance,
                path_type="walkway",
                is_accessible=self.is_accessible
            )
            self.campus_data.add_path(new_path)
            
            # Update connections in both locations
            if end_id not in start_loc.connections:
                start_loc.connections.append(end_id)
            if start_id not in end_loc.connections:
                end_loc.connections.append(start_id)
            
            print(f"Created edge: {start_id} -> {end_id} (Distance: {distance:.1f}m)")

    def _remove_node(self, node_id: str) -> None:
        """Remove a node and all its connected edges"""
        if node_id in self.campus_data.locations:
            # Remove all paths connected to this node
            self.campus_data.paths = [
                path for path in self.campus_data.paths 
                if path.start_id != node_id and path.end_id != node_id
            ]
            
            # Remove node from other nodes' connections
            for location in self.campus_data.locations.values():
                if node_id in location.connections:
                    location.connections.remove(node_id)
            
            # Remove the node itself
            del self.campus_data.locations[node_id]

    def _find_node_at_position(self, normalized_pos: Tuple[float, float]) -> Optional[str]:
        """Find if there's a node at the given position"""
        for loc_id, location in self.campus_data.locations.items():
            distance = ((normalized_pos[0] - location.x) ** 2 + 
                       (normalized_pos[1] - location.y) ** 2) ** 0.5
            if distance < 0.02:  # Threshold for clicking near a node
                return loc_id
        return None

    def get_current_edge_drawing(self) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """Get the coordinates of the edge currently being drawn"""
        if self.drawing_edge and self.edge_start:
            start_loc = self.campus_data.locations[self.edge_start]
            return ((start_loc.x, start_loc.y), None)
        return None

    def save_map(self) -> None:
        """Save the current map to JSON"""
        data_dir = PathLib(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        
        self.campus_data.save_to_json(data_dir / "locations.json")
        print("Map saved successfully!")

    def load_map(self) -> None:
        """Load map from JSON"""
        data_dir = PathLib(__file__).parent.parent.parent / "data"
        json_path = data_dir / "locations.json"
        
        if json_path.exists():
            self.campus_data = CampusData.load_from_json(json_path)
            print("Map loaded successfully!")
        else:
            print("No saved map found.")

    def _find_edge_at_position(self, pos: Tuple[float, float]) -> Optional[Tuple[str, str]]:
        """Find if there's an edge at the given position"""
        for path in self.campus_data.paths:
            start_loc = self.campus_data.locations[path.start_id]
            end_loc = self.campus_data.locations[path.end_id]
            
            # Calculate distance from point to line segment
            distance = self._point_to_line_distance(
                pos,
                (start_loc.x, start_loc.y),
                (end_loc.x, end_loc.y)
            )
            
            if distance < self.edge_click_threshold:
                return (path.start_id, path.end_id)
        return None

    def _point_to_line_distance(self, point: Tuple[float, float], 
                              line_start: Tuple[float, float], 
                              line_end: Tuple[float, float]) -> float:
        """Calculate the distance from a point to a line segment"""
        x, y = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Calculate the length of the line segment
        line_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        
        if line_length == 0:
            return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
            
        # Calculate the distance from point to line
        t = max(0, min(1, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / (line_length ** 2)))
        
        # Find the nearest point on the line segment
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        # Calculate the distance from the point to the nearest point on the line
        return ((x - proj_x) ** 2 + (y - proj_y) ** 2) ** 0.5

    def _remove_edge(self, edge: Tuple[str, str]) -> None:
        """Remove an edge and update connections"""
        start_id, end_id = edge
        
        # Remove the path
        self.campus_data.paths = [
            path for path in self.campus_data.paths 
            if not ((path.start_id == start_id and path.end_id == end_id) or 
                   (path.start_id == end_id and path.end_id == start_id))
        ]
        
        # Update connections in both locations
        if start_id in self.campus_data.locations and end_id in self.campus_data.locations:
            start_loc = self.campus_data.locations[start_id]
            end_loc = self.campus_data.locations[end_id]
            
            if end_id in start_loc.connections:
                start_loc.connections.remove(end_id)
            if start_id in end_loc.connections:
                end_loc.connections.remove(start_id)
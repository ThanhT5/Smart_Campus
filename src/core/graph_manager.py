import networkx as nx  # Import NetworkX for graph representation
from typing import Dict, List, Optional  # Import necessary types for type hinting
from data.campus_data import CampusData  # Import CampusData class to manage campus locations and paths

class GraphManager:
    """Manages the campus graph representation using NetworkX."""
    
    def __init__(self, campus_data: CampusData):
        """
        Initialize the GraphManager with campus data.
        
        Args:
            campus_data (CampusData): The campus data containing locations and paths.
        """
        self.campus_data = campus_data  # Store the campus data
        self.graph = nx.Graph()  # Initialize an empty NetworkX graph
        self._build_graph()  # Build the graph from campus data
        
    def _build_graph(self) -> None:
        """Builds the NetworkX graph from campus data."""
        # Add nodes (locations) to the graph
        for loc_id, location in self.campus_data.locations.items():
            self.graph.add_node(
                loc_id,  # Unique identifier for the node
                name=location.name,  # Name of the location
                type=location.type,  # Type of the location (e.g., building, waypoint)
                x=location.x,  # X coordinate of the location
                y=location.y,  # Y coordinate of the location
                is_accessible=getattr(location, 'is_accessible', True)  # Accessibility status
            )
        
        # Add edges (connections) between nodes
        for loc_id, location in self.campus_data.locations.items():
            for connected_id in location.connections:  # Iterate through connected locations
                if connected_id in self.campus_data.locations:  # Check if the connected location exists
                    # Add edge if both locations exist
                    self.graph.add_edge(loc_id, connected_id)  # Create an edge between the two locations
    
    def get_location_info(self, location_id: str) -> Optional[Dict]:
        """
        Get information about a specific location.
        
        Args:
            location_id (str): The ID of the location to retrieve information for.
        
        Returns:
            Optional[Dict]: A dictionary containing location information, or None if not found.
        """
        if location_id in self.graph:  # Check if the location exists in the graph
            return dict(self.graph.nodes[location_id])  # Return the node's attributes as a dictionary
        return None  # Return None if the location is not found
    
    def get_connected_locations(self, location_id: str) -> List[str]:
        """
        Get list of locations connected to the given location.
        
        Args:
            location_id (str): The ID of the location to find connections for.
        
        Returns:
            List[str]: A list of IDs of connected locations.
        """
        if location_id in self.graph:  # Check if the location exists in the graph
            return list(self.graph.neighbors(location_id))  # Return a list of connected location IDs
        return []  # Return an empty list if the location is not found

import networkx as nx
from typing import Dict, List, Optional
from data.campus_data import CampusData

class GraphManager:
    """Manages the campus graph representation using NetworkX."""
    
    def __init__(self, campus_data: CampusData):
        self.campus_data = campus_data
        self.graph = nx.Graph()
        self._build_graph()
        
    def _build_graph(self) -> None:
        """Builds the NetworkX graph from campus data."""
        # Add nodes (locations)
        for loc_id, location in self.campus_data.locations.items():
            self.graph.add_node(
                loc_id,
                name=location.name,
                type=location.type,
                x=location.x,
                y=location.y,
                is_accessible=getattr(location, 'is_accessible', True)
            )
        
        # Add edges (connections)
        for loc_id, location in self.campus_data.locations.items():
            for connected_id in location.connections:
                if connected_id in self.campus_data.locations:
                    # Add edge if both locations exist
                    self.graph.add_edge(loc_id, connected_id)
    
    def get_location_info(self, location_id: str) -> Optional[Dict]:
        """Get information about a specific location."""
        if location_id in self.graph:
            return dict(self.graph.nodes[location_id])
        return None
    
    def get_connected_locations(self, location_id: str) -> List[str]:
        """Get list of locations connected to the given location."""
        if location_id in self.graph:
            return list(self.graph.neighbors(location_id))
        return []

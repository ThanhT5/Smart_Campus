from algorithms.graph import GraphManager
from navigation.nav_state import NavigationState

class NavigationHandler:
    def __init__(self, graph_manager: GraphManager, console_panel):
        self.graph = graph_manager
        self.nav_state = NavigationState()
        self.console_panel = console_panel
        
    def handle_node_click(self, node_id: str) -> None:
        """Handle node selection in navigation mode"""
        if not self.nav_state.start_node:
            self.nav_state.start_node = node_id
        elif not self.nav_state.end_node:
            self.nav_state.end_node = node_id
            self._calculate_path()
    
    def reset_selection(self) -> None:
        """Reset the current navigation selection"""
        self.nav_state.start_node = None
        self.nav_state.end_node = None
        self.nav_state.current_path = None
    
    def toggle_path_type(self) -> None:
        """Toggle between fastest and accessible paths"""
        self.nav_state.path_type = ("accessible" if self.nav_state.path_type == "fastest" 
                                   else "fastest")
        if self.nav_state.start_node and self.nav_state.end_node:
            self._calculate_path()
    
    def _calculate_path(self) -> None:
        """Calculate path based on current settings and selected algorithm"""
        accessible_only = self.nav_state.path_type == "accessible"
        
        # Get algorithm from console panel
        algorithm = self.console_panel.selected_algorithm  # You'll need to pass console_panel reference
        
        if algorithm == "Dijkstra's Algorithm":
            result = self.graph.dijkstra(
                self.nav_state.start_node,
                self.nav_state.end_node,
                accessible_only=accessible_only
            )
            if result:
                path, distance = result
                self.nav_state.current_path = {
                    'nodes': path,
                    'distance': distance
                }
        
        elif algorithm == "Breadth-First Search":
            path = self.graph.bfs(
                self.nav_state.start_node,
                self.nav_state.end_node,
                accessible_only=accessible_only
            )
            if path:
                self.nav_state.current_path = {
                    'nodes': path,
                    'distance': None  # BFS doesn't calculate distances
                }
        
        elif algorithm == "Depth-First Search":
            path = self.graph.dfs(
                self.nav_state.start_node,
                self.nav_state.end_node,
                accessible_only=accessible_only
            )
            if path:
                self.nav_state.current_path = {
                    'nodes': path,
                    'distance': None  # DFS doesn't calculate distances
                }
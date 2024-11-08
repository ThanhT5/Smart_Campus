from typing import Dict, List, Set, Optional, Tuple  # Import necessary types for type hinting
from data.campus_data import CampusData  # Import CampusData class to manage campus locations and paths
import networkx as nx  # Import NetworkX for graph representation

class GraphManager:
    def __init__(self, campus_data: CampusData):
        """Initialize the GraphManager with campus data."""
        print("\nInitializing GraphManager:")  # Debug message for initialization
        self.campus_data = campus_data  # Store campus data
        print(f"Campus data contains {len(self.campus_data.locations)} locations and {len(self.campus_data.paths)} paths")  # Print number of locations and paths
        self.G = self._create_networkx_graph()  # Create the graph from campus data
        self._verify_graph()  # Verify the created graph structure

    def _create_networkx_graph(self) -> nx.Graph:
        """Create a NetworkX graph from campus data."""
        G = nx.Graph()  # Initialize an empty NetworkX graph
        
        print("\nCreating NetworkX Graph:")  # Debug message for graph creation
        
        # Add nodes to the graph
        for loc_id, location in self.campus_data.locations.items():
            G.add_node(loc_id, pos=(location.x, location.y))  # Add node with position
            print(f"Added node: {loc_id}")  # Debug message for added node
        
        # Add edges to the graph
        for path in self.campus_data.paths:
            G.add_edge(path.start_id, path.end_id, weight=path.distance)  # Add edge with weight
            print(f"Added edge: {path.start_id} -> {path.end_id} (distance: {path.distance})")  # Debug message for added edge
        
        return G  # Return the created graph

    def _verify_graph(self):
        """Verify graph structure and print debug info."""
        print("\nGraph Verification:")  # Debug message for verification
        print(f"Number of nodes: {self.G.number_of_nodes()}")  # Print number of nodes
        print(f"Number of edges: {self.G.number_of_edges()}")  # Print number of edges
        print(f"Nodes: {list(self.G.nodes())}")  # Print list of nodes
        print(f"Sample of edges: {list(self.G.edges())[:5]}")  # Print sample of edges
    
    def get_edge_list(self) -> List[Tuple[str, str]]:
        """Get list of edges for drawing."""
        return list(self.G.edges())  # Return list of edges
        
    def get_path_edges(self, path: List[str]) -> List[Tuple[str, str]]:
        """Convert path node list to edge list for highlighting."""
        edges = []  # Initialize list for edges
        for i in range(len(path) - 1):
            edges.append((path[i], path[i + 1]))  # Append edge from path
        return edges  # Return list of edges

    def get_adjacent_nodes(self, node_id: str, accessible_only: bool = False) -> List[Tuple[str, float]]:
        """Get adjacent nodes and their distances."""
        adjacent = []  # Initialize list for adjacent nodes
        for path in self.campus_data.paths:
            if path.start_id == node_id:  # Check if path starts from the node
                if not accessible_only or path.is_accessible:  # Check accessibility if required
                    adjacent.append((path.end_id, path.distance))  # Append adjacent node and distance
            elif path.end_id == node_id:  # Check if path ends at the node
                if not accessible_only or path.is_accessible:  # Check accessibility if required
                    adjacent.append((path.start_id, path.distance))  # Append adjacent node and distance
        return adjacent  # Return list of adjacent nodes

    def get_adjacency_list(self, accessible_only: bool = False) -> Dict[str, List[Tuple[str, float]]]:
        """Convert campus data to adjacency list format."""
        adj_list = {}  # Initialize adjacency list
        for node_id in self.campus_data.locations:
            adj_list[node_id] = self.get_adjacent_nodes(node_id, accessible_only)  # Populate adjacency list
        return adj_list  # Return adjacency list

    def bfs(self, start_id: str, end_id: str, accessible_only: bool = False) -> Optional[List[str]]:
        """Breadth-First Search implementation using NetworkX."""
        if start_id not in self.G or end_id not in self.G:  # Check if start and end nodes are in the graph
            return None  # Return None if nodes are not found

        if accessible_only:
            # Create a subgraph with only accessible edges
            accessible_edges = [(u, v) for (u, v, d) in self.G.edges(data=True) if d['is_accessible']]  # Filter accessible edges
            G_accessible = self.G.edge_subgraph(accessible_edges)  # Create subgraph with accessible edges
            try:
                path = nx.single_source_shortest_path(G_accessible, start_id)[end_id]  # Find path in subgraph
                return path  # Return found path
            except KeyError:
                return None  # Return None if path not found
        else:
            try:
                path = nx.single_source_shortest_path(self.G, start_id)[end_id]  # Find path in full graph
                return path  # Return found path
            except KeyError:
                return None  # Return None if path not found

    def dfs(self, start_id: str, end_id: str, accessible_only: bool = False) -> Optional[List[str]]:
        """Depth-First Search implementation."""
        if start_id not in self.G or end_id not in self.G:  # Check if start and end nodes are in the graph
            return None  # Return None if nodes are not found

        def dfs_path(current, target, visited):
            """Recursive helper function for DFS."""
            if current == target:  # Check if current node is the target
                return [current]  # Return path to target
            
            visited.add(current)  # Mark current node as visited
            for neighbor in self.G.neighbors(current):  # Iterate through neighbors
                if neighbor not in visited:  # Check if neighbor is unvisited
                    path = dfs_path(neighbor, target, visited)  # Recursive call
                    if path:  # If path is found
                        return [current] + path  # Return path including current node
            return None  # Return None if no path found

        return dfs_path(start_id, end_id, set())  # Start DFS from the initial node

    def dfs_all_paths(self, start_id: str, end_id: str, accessible_only: bool = False) -> List[List[str]]:
        """Find all possible paths between two nodes using DFS."""
        if start_id not in self.G or end_id not in self.G:  # Check if start and end nodes are in the graph
            return []  # Return empty list if nodes are not found

        def dfs_paths(current, target, path, visited, all_paths):
            """Recursive helper function to find all paths."""
            path.append(current)  # Add current node to path
            
            if current == target:  # Check if current node is the target
                all_paths.append(path.copy())  # Save a copy of the path
            else:
                for neighbor in self.G.neighbors(current):  # Iterate through neighbors
                    if neighbor not in visited:  # Check if neighbor is unvisited
                        visited.add(neighbor)  # Mark neighbor as visited
                        dfs_paths(neighbor, target, path, visited, all_paths)  # Recursive call
                        visited.remove(neighbor)  # Backtrack: unmark neighbor
            
            path.pop()  # Backtrack: remove current node from path

        all_paths = []  # Initialize list to store all found paths
        dfs_paths(start_id, end_id, [], {start_id}, all_paths)  # Start DFS for all paths
        
        # Print all paths and their characteristics
        print(f"\nFound {len(all_paths)} possible paths:")  # Debug message for found paths
        for i, path in enumerate(all_paths):  # Iterate through found paths
            # Calculate path distance
            distance = sum(self.G[path[j]][path[j+1]]['weight'] 
                          for j in range(len(path)-1))  # Sum weights of edges in the path
            # Count landmarks (non-waypoint nodes)
            landmarks = sum(1 for node in path 
                           if not node.startswith('waypoint_'))  # Count non-waypoint nodes
            
            print(f"\nPath {i+1}:")  # Debug message for path
            print(f"Route: {' -> '.join(path)}")  # Print route
            print(f"Distance: {distance:.2f} meters")  # Print distance
            print(f"Landmarks passed: {landmarks}")  # Print number of landmarks
        
        return all_paths  # Return all found paths

    def dijkstra(self, start_id: str, end_id: str, accessible_only: bool = False) -> Optional[Tuple[List[str], float]]:
        """Dijkstra's algorithm implementation using NetworkX."""
        print(f"\nDijkstra Debug:")  # Debug message for Dijkstra's algorithm
        print(f"Looking for path from {start_id} to {end_id}")  # Print start and end nodes
        
        if start_id not in self.G or end_id not in self.G:  # Check if start and end nodes are in the graph
            print(f"Start node in graph: {start_id in self.G}")  # Print existence of start node
            print(f"End node in graph: {end_id in self.G}")  # Print existence of end node
            return None  # Return None if nodes are not found
        
        try:
            path = nx.shortest_path(self.G, start_id, end_id, weight='weight')  # Find shortest path
            distance = nx.shortest_path_length(self.G, start_id, end_id, weight='weight')  # Calculate path length
            print(f"Found path: {path}")  # Print found path
            print(f"Path distance: {distance}")  # Print path distance
            return path, distance  # Return path and distance
        except nx.NetworkXNoPath:
            print(f"NetworkX could not find a path between nodes!")  # Debug message for no path found
            return None  # Return None if no path exists

    def reinitialize_with_data(self, campus_data: CampusData):
        """Reinitialize the graph with new campus data."""
        self.campus_data = campus_data  # Update campus data
        self.G = self._create_networkx_graph()  # Recreate the graph with new data
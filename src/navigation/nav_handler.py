from algorithms.graph import GraphManager  # Import the GraphManager for graph-related operations
from navigation.nav_state import NavigationState  # Import the NavigationState to manage navigation state
import networkx as nx  # Import NetworkX for graph algorithms

class NavigationHandler:
    def __init__(self, graph_manager: GraphManager, console_panel):
        """Initialize the NavigationHandler with a graph manager and console panel."""
        print("\nInitializing NavigationHandler")  # Debug message for initialization
        self.graph = graph_manager  # Store the graph manager instance
        self.nav_state = NavigationState()  # Initialize navigation state
        self.console_panel = console_panel  # Store the console panel reference
        self.accessibility = False  # Flag to indicate if accessibility mode is enabled
        print(f"Navigation handler initialized with graph containing {self.graph.G.number_of_nodes()} nodes")  # Debug message for node count
        
    def handle_node_click(self, node_id: str) -> None:
        """Handle node selection in navigation mode."""
        print(f"\nHandling node click: {node_id}")  # Debug message for node click
        print(f"Graph has {self.graph.G.number_of_nodes()} nodes")  # Debug message for graph node count
        print(f"Node exists in graph: {node_id in self.graph.G}")  # Debug message for node existence
        
        # Check if start node is not set
        if not self.nav_state.start_node:
            self.nav_state.start_node = node_id  # Set the start node
            print(f"Set start node: {node_id}")  # Debug message for setting start node
        # Check if end node is not set
        elif not self.nav_state.end_node:
            self.nav_state.end_node = node_id  # Set the end node
            print(f"Set end node: {node_id}")  # Debug message for setting end node
            self._calculate_path()  # Calculate the path after setting end node
    
    def reset_selection(self) -> None:
        """Reset the current navigation selection."""
        self.nav_state.start_node = None  # Clear the start node
        self.nav_state.end_node = None  # Clear the end node
        self.nav_state.current_path = None  # Clear the current path
    
    def _calculate_path(self) -> None:
        """Calculate path based on current settings and selected algorithm."""
        print(f"\nCalculating path from {self.nav_state.start_node} to {self.nav_state.end_node}")  # Debug message for path calculation
        print(f"Using algorithm: {self.console_panel.selected_algorithm}")  # Debug message for selected algorithm
        print(f"Accessibility mode: {'ON' if self.accessibility else 'OFF'}")  # Debug message for accessibility mode
        
        algorithm = self.console_panel.selected_algorithm  # Get the selected algorithm
        result = None  # Initialize result variable
        
        # Check if accessibility mode is not enabled
        if not self.accessibility:
            # Check for Dijkstra's Algorithm
            if algorithm == "Dijkstra's Algorithm":
                result = self.graph.dijkstra(  # Call Dijkstra's algorithm
                    self.nav_state.start_node,
                    self.nav_state.end_node
                )
                if result:  # If a result is returned
                    path, distance = result  # Unpack the path and distance
                    self.nav_state.current_path = {  # Store the current path
                        'nodes': path,
                        'distance': distance
                    }
            
            # Check for Breadth-First Search
            elif algorithm == "Breadth-First Search":
                path = self.graph.bfs(  # Call BFS algorithm
                    self.nav_state.start_node,
                    self.nav_state.end_node
                )
                if path:  # If a path is found
                    # Calculate distance for BFS path
                    distance = sum(self.graph.G[path[i]][path[i+1]]['weight'] 
                                for i in range(len(path)-1))  # Sum weights of edges in the path
                    self.nav_state.current_path = {  # Store the current path
                        'nodes': path,
                        'distance': distance
                    }
            
            # Check for Depth-First Search
            elif algorithm == "Depth-First Search":
                # Get all possible paths
                all_paths = self.graph.dfs_all_paths(  # Call DFS to get all paths
                    self.nav_state.start_node,
                    self.nav_state.end_node
                )
                
                if all_paths:  # If any paths are found
                    # For now, choose the path with most landmarks
                    paths_with_metrics = []  # List to store paths with metrics
                    for path in all_paths:  # Iterate through all paths
                        distance = sum(self.graph.G[path[i]][path[i+1]]['weight'] 
                                    for i in range(len(path)-1))  # Calculate distance
                        landmarks = sum(1 for node in path 
                                    if not node.startswith('waypoint_'))  # Count landmarks
                        paths_with_metrics.append((path, distance, landmarks))  # Append metrics to list
                    
                    # Sort by number of landmarks (could be changed to other criteria)
                    paths_with_metrics.sort(key=lambda x: x[2], reverse=True)  # Sort paths by landmarks
                    best_path = paths_with_metrics[0]  # Select the best path
                    
                    self.nav_state.current_path = {  # Store the current path
                        'nodes': best_path[0],
                        'distance': best_path[1]
                    }
                    print(f"\nChose path with most landmarks:")  # Debug message for chosen path
                    print(f"Path: {' -> '.join(best_path[0])}")  # Print the path
                    print(f"Distance: {best_path[1]:.2f} meters")  # Print the distance
                    print(f"Landmarks: {best_path[2]}")  # Print the number of landmarks
        else:  # If accessibility mode is enabled
            try:
                # Create a subgraph with only accessible paths
                accessible_edges = []  # List to store accessible edges
                for path in self.graph.campus_data.paths:  # Iterate through all paths
                    if path.is_accessible:  # Check if the path is accessible
                        accessible_edges.append((path.start_id, path.end_id))  # Append accessible edges
                
                if not accessible_edges:  # If no accessible edges are found
                    print("No accessible paths found in the graph!")  # Debug message
                    self.nav_state.current_path = None  # Clear current path
                    return  # Exit the function
                
                # Create accessible subgraph
                G_accessible = self.graph.G.edge_subgraph(accessible_edges)  # Create subgraph of accessible edges
                
                # Check if both nodes are in the accessible subgraph
                if (self.nav_state.start_node not in G_accessible or 
                    self.nav_state.end_node not in G_accessible):
                    print("Start or end node not connected to any accessible paths!")  # Debug message
                    self.nav_state.current_path = None  # Clear current path
                    return  # Exit the function
                
                # Check for Dijkstra's Algorithm in accessibility mode
                if algorithm == "Dijkstra's Algorithm":
                    try:
                        path = nx.shortest_path(G_accessible,  # Find shortest path in accessible graph
                            self.nav_state.start_node,
                            self.nav_state.end_node,
                            weight='weight')
                        distance = nx.shortest_path_length(G_accessible,  # Calculate path length
                            self.nav_state.start_node,
                            self.nav_state.end_node,
                            weight='weight')
                        self.nav_state.current_path = {  # Store the current path
                            'nodes': path,
                            'distance': distance
                        }
                    except (nx.NetworkXNoPath, nx.NodeNotFound):  # Handle exceptions
                        print("No accessible path found between selected nodes!")  # Debug message
                        self.nav_state.current_path = None  # Clear current path
                        
                # Check for Breadth-First Search in accessibility mode
                elif algorithm == "Breadth-First Search":
                    try:
                        path = nx.single_source_shortest_path(G_accessible,  # Find path using BFS
                            self.nav_state.start_node)[self.nav_state.end_node]
                        # Calculate distance for BFS path
                        distance = sum(self.graph.G[path[i]][path[i+1]]['weight'] 
                                     for i in range(len(path)-1))  # Sum weights of edges in the path
                        self.nav_state.current_path = {  # Store the current path
                            'nodes': path,
                            'distance': distance
                        }
                    except (nx.NetworkXNoPath, nx.NodeNotFound, KeyError):  # Handle exceptions
                        print("No accessible path found between selected nodes!")  # Debug message
                        self.nav_state.current_path = None  # Clear current path
                        
                # Check for Depth-First Search in accessibility mode
                elif algorithm == "Depth-First Search":
                    # Get all possible accessible paths
                    all_paths = []  # List to store all accessible paths
                    def dfs_accessible_paths(current, target, path, visited):
                        """Recursive function to find all accessible paths using DFS."""
                        path.append(current)  # Add current node to path
                        if current == target:  # If target is reached
                            all_paths.append(path.copy())  # Append the found path
                        else:
                            for neighbor in G_accessible.neighbors(current):  # Iterate through neighbors
                                if neighbor not in visited:  # Check if neighbor is not visited
                                    visited.add(neighbor)  # Mark neighbor as visited
                                    dfs_accessible_paths(neighbor, target, path, visited)  # Recur for neighbor
                                    visited.remove(neighbor)  # Unmark neighbor after recursion
                        path.pop()  # Remove current node from path

                    try:
                        dfs_accessible_paths(self.nav_state.start_node,  # Start DFS from start node
                                           self.nav_state.end_node, 
                                           [],  # Initialize empty path
                                           {self.nav_state.start_node})  # Initialize visited set
                        
                        if all_paths:  # If any accessible paths are found
                            # Calculate metrics for each path
                            paths_with_metrics = []  # List to store paths with metrics
                            for path in all_paths:  # Iterate through all paths
                                distance = sum(self.graph.G[path[i]][path[i+1]]['weight'] 
                                             for i in range(len(path)-1))  # Calculate distance
                                landmarks = sum(1 for node in path 
                                              if not node.startswith('waypoint_'))  # Count landmarks
                                paths_with_metrics.append((path, distance, landmarks))  # Append metrics to list
                            
                            # Sort by number of landmarks
                            paths_with_metrics.sort(key=lambda x: x[2], reverse=True)  # Sort paths by landmarks
                            best_path = paths_with_metrics[0]  # Select the best path
                            
                            self.nav_state.current_path = {  # Store the current path
                                'nodes': best_path[0],
                                'distance': best_path[1]
                            }
                            print(f"\nChose accessible path with most landmarks:")  # Debug message for chosen path
                            print(f"Path: {' -> '.join(best_path[0])}")  # Print the path
                            print(f"Distance: {best_path[1]:.2f} meters")  # Print the distance
                            print(f"Landmarks: {best_path[2]}")  # Print the number of landmarks
                        else:  # If no accessible paths are found
                            print("No accessible path found between selected nodes!")  # Debug message
                            self.nav_state.current_path = None  # Clear current path
                    except (nx.NetworkXNoPath, nx.NodeNotFound) as e:  # Handle exceptions
                        print(f"Error finding accessible path: {str(e)}")  # Debug message
                        self.nav_state.current_path = None  # Clear current path
                        
            except Exception as e:  # Handle any other exceptions
                print(f"Error finding accessible path: {str(e)}")  # Debug message
                self.nav_state.current_path = None  # Clear current path
        
        # Print results
        if self.nav_state.current_path:  # If a path is found
            print(f"Path found: {' -> '.join(self.nav_state.current_path['nodes'])}")  # Print the path
            print(f"Total distance: {self.nav_state.current_path['distance']:.2f} meters")  # Print the total distance
        else:  # If no path is found
            print("No path found between selected nodes!")  # Debug message
            print("No path is currently set in navigation state")  # Debug message
            # Reset node selection when no path is found
            self.reset_selection()  # Clear selections
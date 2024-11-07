from typing import Dict, List, Set, Optional, Tuple
from data.campus_data import CampusData
from collections import deque
import heapq

class GraphManager:
    def __init__(self, campus_data: CampusData):
        self.campus_data = campus_data
        
    def get_adjacent_nodes(self, node_id: str, accessible_only: bool = False) -> List[Tuple[str, float]]:
        """Get adjacent nodes and their distances"""
        adjacent = []
        for path in self.campus_data.paths:
            if path.start_id == node_id:
                if not accessible_only or path.is_accessible:
                    adjacent.append((path.end_id, path.distance))
            elif path.end_id == node_id:
                if not accessible_only or path.is_accessible:
                    adjacent.append((path.start_id, path.distance))
        return adjacent

    def get_adjacency_list(self, accessible_only: bool = False) -> Dict[str, List[Tuple[str, float]]]:
        """Convert campus data to adjacency list format"""
        adj_list = {}
        for node_id in self.campus_data.locations:
            adj_list[node_id] = self.get_adjacent_nodes(node_id, accessible_only)
        return adj_list

    def bfs(self, start_id: str, end_id: str, accessible_only: bool = False) -> Optional[List[str]]:
        """Breadth-First Search implementation"""
        if start_id not in self.campus_data.locations or end_id not in self.campus_data.locations:
            return None

        queue = deque([[start_id]])
        visited = {start_id}

        while queue:
            path = queue.popleft()
            node = path[-1]

            if node == end_id:
                return path

            for next_node, _ in self.get_adjacent_nodes(node, accessible_only):
                if next_node not in visited:
                    visited.add(next_node)
                    new_path = list(path)
                    new_path.append(next_node)
                    queue.append(new_path)

        return None

    def dfs(self, start_id: str, end_id: str, accessible_only: bool = False) -> Optional[List[str]]:
        """Depth-First Search implementation"""
        def dfs_recursive(current: str, visited: Set[str], path: List[str]) -> Optional[List[str]]:
            if current == end_id:
                return path

            for next_node, _ in self.get_adjacent_nodes(current, accessible_only):
                if next_node not in visited:
                    visited.add(next_node)
                    result = dfs_recursive(next_node, visited, path + [next_node])
                    if result:
                        return result
            return None

        if start_id not in self.campus_data.locations or end_id not in self.campus_data.locations:
            return None

        visited = {start_id}
        return dfs_recursive(start_id, visited, [start_id])

    def dijkstra(self, start_id: str, end_id: str, accessible_only: bool = False) -> Optional[Tuple[List[str], float]]:
        """Dijkstra's algorithm implementation"""
        if start_id not in self.campus_data.locations or end_id not in self.campus_data.locations:
            return None

        distances = {node: float('infinity') for node in self.campus_data.locations}
        distances[start_id] = 0
        pq = [(0, start_id)]
        previous = {node: None for node in self.campus_data.locations}

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_node == end_id:
                path = []
                while current_node:
                    path.append(current_node)
                    current_node = previous[current_node]
                return path[::-1], current_distance

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in self.get_adjacent_nodes(current_node, accessible_only):
                distance = current_distance + weight

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))

        return None
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class Location:
    id: str
    name: str
    x: float
    y: float
    type: str  # "building", "waypoint", "entrance"
    full_name: str = ""
    is_accessible: bool = True
    is_waypoint: bool = False
    connections: List[str] = None

    def __post_init__(self):
        if self.connections is None:
            self.connections = []

@dataclass
class Path:
    start_id: str
    end_id: str
    distance: float
    path_type: str = "walkway"
    is_accessible: bool = True

class CampusData:
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.paths: List[Path] = []

    def add_location(self, location: Location) -> None:
        """Add a new location to the campus."""
        if location.connections is None:
            location.connections = []
        self.locations[location.id] = location

    def add_path(self, path: Path) -> None:
        """Add a new path between locations."""
        self.paths.append(path)

    def get_adjacent_locations(self, location_id: str) -> List[Tuple[str, float]]:
        """Get all locations adjacent to the given location with their distances."""
        adjacent = []
        for path in self.paths:
            if path.start_id == location_id:
                adjacent.append((path.end_id, path.distance))
            elif path.end_id == location_id:
                adjacent.append((path.start_id, path.distance))
        return adjacent

    def save_to_json(self, filepath: Path) -> None:
        """Save campus data to a JSON file."""
        data = {
            "locations": [vars(loc) for loc in self.locations.values()],
            "paths": [vars(path) for path in self.paths]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load_from_json(cls, filepath: Path) -> 'CampusData':
        """Load campus data from a JSON file."""
        campus_data = cls()
        with open(filepath, 'r') as f:
            data = json.load(f)

        for loc_data in data["locations"]:
            location = Location(**loc_data)
            campus_data.add_location(location)

        for path_data in data["paths"]:
            path = Path(**path_data)
            campus_data.add_path(path)

        return campus_data

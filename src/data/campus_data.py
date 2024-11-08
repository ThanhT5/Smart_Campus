# Import necessary modules for type hinting, data classes, JSON handling, and file path management
from typing import Dict, List, Tuple
from dataclasses import dataclass
import json
from pathlib import Path

# Define a data class for Location to represent a place on campus
@dataclass
class Location:
    id: str  # Unique identifier for the location
    name: str  # Name of the location
    x: float  # X coordinate for the location
    y: float  # Y coordinate for the location
    type: str  # Type of location (e.g., "building", "waypoint", "entrance")
    full_name: str = ""  # Full name of the location (optional)
    is_accessible: bool = True  # Accessibility status of the location
    is_waypoint: bool = False  # Indicates if the location is a waypoint
    connections: List[str] = None  # List of connected location IDs

    # Post-initialization to ensure connections is initialized as an empty list if not provided
    def __post_init__(self):
        if self.connections is None:
            self.connections = []  # Initialize connections to an empty list

# Define a data class for Path to represent a connection between two locations
@dataclass
class Path:
    start_id: str  # ID of the starting location
    end_id: str  # ID of the ending location
    distance: float  # Distance between the two locations
    path_type: str = "walkway"  # Type of path (default is "walkway")
    is_accessible: bool = True  # Accessibility status of the path

# Class to manage campus data including locations and paths
class CampusData:
    def __init__(self):
        # Initialize dictionaries to hold locations and paths
        self.locations: Dict[str, Location] = {}  # Dictionary of locations keyed by their IDs
        self.paths: List[Path] = []  # List to hold paths between locations

    def add_location(self, location: Location) -> None:
        """Add a new location to the campus."""
        # Ensure connections are initialized
        if location.connections is None:
            location.connections = []  # Initialize connections if None
        self.locations[location.id] = location  # Add the location to the dictionary

    def add_path(self, path: Path) -> None:
        """Add a new path between locations."""
        self.paths.append(path)  # Append the new path to the list of paths

    def get_adjacent_locations(self, location_id: str) -> List[Tuple[str, float]]:
        """Get all locations adjacent to the given location with their distances."""
        adjacent = []  # List to hold adjacent locations
        # Iterate through all paths to find adjacent locations
        for path in self.paths:
            if path.start_id == location_id:
                adjacent.append((path.end_id, path.distance))  # Add end location and distance
            elif path.end_id == location_id:
                adjacent.append((path.start_id, path.distance))  # Add start location and distance
        return adjacent  # Return the list of adjacent locations

    def save_to_json(self, filepath: Path) -> None:
        """Save campus data to a JSON file."""
        # Prepare data for saving
        data = {
            "locations": [vars(loc) for loc in self.locations.values()],  # Convert locations to dicts
            "paths": [vars(path) for path in self.paths]  # Convert paths to dicts
        }
        # Write data to the specified JSON file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)  # Save data with indentation for readability

    @classmethod
    def load_from_json(cls, filepath: Path) -> 'CampusData':
        """Load campus data from a JSON file."""
        campus_data = cls()  # Create a new instance of CampusData
        print("\nLoading JSON data:")  # Debug message for loading data
        
        # Open and read the JSON file
        with open(filepath, 'r') as f:
            data = json.load(f)  # Load JSON data
            print(f"Raw JSON data: {data.keys()}")  # Print keys of the loaded data
        
        # Load locations from the JSON data
        print("\nLoading locations:")
        for loc_data in data.get("locations", []):
            location = Location(**loc_data)  # Create a Location instance from the data
            campus_data.add_location(location)  # Add the location to campus data
            print(f"Loaded location: {location.id}")  # Debug message for loaded location
        
        # Load paths from the JSON data
        print("\nLoading paths:")
        for path_data in data.get("paths", []):
            path = Path(**path_data)  # Create a Path instance from the data
            campus_data.add_path(path)  # Add the path to campus data
            print(f"Loaded path: {path.start_id} -> {path.end_id}")  # Debug message for loaded path
        
        # Print summary of loaded data
        print(f"\nTotal locations loaded: {len(campus_data.locations)}")  # Count of loaded locations
        print(f"Total paths loaded: {len(campus_data.paths)}")  # Count of loaded paths
        
        return campus_data  # Return the populated CampusData instance

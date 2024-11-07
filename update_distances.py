import json
from pathlib import Path

def calculate_distance(start_pos, end_pos, scale_factor=750):
    """Calculate the Euclidean distance between two points"""
    dx = (end_pos['x'] - start_pos['x']) * scale_factor
    dy = (end_pos['y'] - start_pos['y']) * scale_factor
    return round(((dx ** 2 + dy ** 2) ** 0.5), 1)

def update_distances():
    # Load the existing JSON file
    json_path = Path('data/locations.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Create a lookup for locations
    locations = {loc['id']: loc for loc in data['locations']}
    
    # Update distances in paths
    for path in data['paths']:
        start_loc = locations[path['start_id']]
        end_loc = locations[path['end_id']]
        
        # Calculate new distance
        distance = calculate_distance(start_loc, end_loc)
        path['distance'] = distance
    
    # Save the updated JSON file
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)
    
    print("Distances updated successfully!")

if __name__ == "__main__":
    update_distances() 
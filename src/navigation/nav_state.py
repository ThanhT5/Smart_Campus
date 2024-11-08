class NavigationState:
    def __init__(self):
        self.start_node = None
        self.end_node = None
        self.current_path = None
        self.path_colors = {
            "fastest": (0, 255, 0),      # Green
            "accessible": (0, 150, 255),  # Light Blue
            "selected": (255, 165, 0),    # Orange for selected nodes
            "highlight": (255, 255, 0)    # Yellow for hovering
        } 
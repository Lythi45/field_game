"""
Game Configuration Settings
"""

class Config:
    """Global game configuration"""
    
    # Display settings
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768
    FPS = 60
    TITLE = "Isometric Farm Game"
    
    # Isometric settings
    TILE_WIDTH = 64
    TILE_HEIGHT = 32
    TILE_DEPTH = 16  # For 3D effect
    
    # World settings
    WORLD_WIDTH = 50
    WORLD_HEIGHT = 50
    
    # Camera settings
    CAMERA_SPEED = 5
    ZOOM_MIN = 0.5
    ZOOM_MAX = 2.0
    ZOOM_STEP = 0.1
    
    # Colors
    BACKGROUND_COLOR = (34, 139, 34)  # Forest green
    GRID_COLOR = (255, 255, 255, 50)  # Semi-transparent white
    SELECTION_COLOR = (255, 255, 0)   # Yellow
    
    # Game settings
    GAME_SPEED = 1.0
    
    # Debug settings
    DEBUG_MODE = True
    SHOW_GRID = True
    SHOW_COORDINATES = True
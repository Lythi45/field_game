"""
Mathematical utilities for isometric projection and game calculations
"""

import math
from typing import Tuple

class IsometricMath:
    """Utility class for isometric coordinate conversions"""
    
    @staticmethod
    def world_to_screen(world_x: int, world_y: int, tile_width: int = 64, tile_height: int = 32) -> Tuple[int, int]:
        """
        Convert world coordinates to screen coordinates
        
        Args:
            world_x: X coordinate in world space
            world_y: Y coordinate in world space
            tile_width: Width of a tile in pixels
            tile_height: Height of a tile in pixels
            
        Returns:
            Tuple of (screen_x, screen_y)
        """
        screen_x = (world_x - world_y) * (tile_width // 2)
        screen_y = (world_x + world_y) * (tile_height // 2)
        return screen_x, screen_y
    
    @staticmethod
    def screen_to_world(screen_x: int, screen_y: int, tile_width: int = 64, tile_height: int = 32) -> Tuple[int, int]:
        """
        Convert screen coordinates to world coordinates
        
        Args:
            screen_x: X coordinate in screen space
            screen_y: Y coordinate in screen space
            tile_width: Width of a tile in pixels
            tile_height: Height of a tile in pixels
            
        Returns:
            Tuple of (world_x, world_y)
        """
        # Normalize coordinates
        norm_x = screen_x / (tile_width // 2)
        norm_y = screen_y / (tile_height // 2)
        
        # Convert to world coordinates
        world_x = (norm_x + norm_y) / 2
        world_y = (norm_y - norm_x) / 2
        
        return int(world_x), int(world_y)
    
    @staticmethod
    def distance(x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate distance between two points"""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """Clamp a value between min and max"""
        return max(min_val, min(value, max_val))
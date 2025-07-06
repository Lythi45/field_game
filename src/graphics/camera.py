"""
Camera system for handling viewport and scrolling
"""

import pygame
from src.config import Config
from src.utils.math_utils import IsometricMath

class Camera:
    """Handles camera movement, zoom, and viewport management"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Camera position (in screen coordinates)
        self.x = 0
        self.y = 0
        
        # Zoom level
        self.zoom = 1.0
        
        # Camera movement
        self.speed = Config.CAMERA_SPEED
        
        # Viewport center
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2
    
    def move(self, dx: float, dy: float):
        """Move camera by delta amounts"""
        self.x += dx * self.speed
        self.y += dy * self.speed
    
    def set_position(self, x: float, y: float):
        """Set camera position directly"""
        self.x = x
        self.y = y
    
    def zoom_in(self):
        """Zoom in by one step"""
        self.zoom = IsometricMath.clamp(
            self.zoom + Config.ZOOM_STEP,
            Config.ZOOM_MIN,
            Config.ZOOM_MAX
        )
    
    def zoom_out(self):
        """Zoom out by one step"""
        self.zoom = IsometricMath.clamp(
            self.zoom - Config.ZOOM_STEP,
            Config.ZOOM_MIN,
            Config.ZOOM_MAX
        )
    
    def world_to_screen(self, world_x: int, world_y: int) -> tuple:
        """Convert world coordinates to screen coordinates with camera offset"""
        screen_x, screen_y = IsometricMath.world_to_screen(
            world_x, world_y, Config.TILE_WIDTH, Config.TILE_HEIGHT
        )
        
        # Apply zoom
        screen_x *= self.zoom
        screen_y *= self.zoom
        
        # Apply camera offset and center on screen
        final_x = screen_x - self.x + self.center_x
        final_y = screen_y - self.y + self.center_y
        
        return final_x, final_y
    
    def screen_to_world(self, screen_x: int, screen_y: int) -> tuple:
        """Convert screen coordinates to world coordinates with camera offset"""
        # Remove camera offset and centering
        adjusted_x = (screen_x - self.center_x + self.x) / self.zoom
        adjusted_y = (screen_y - self.center_y + self.y) / self.zoom
        
        return IsometricMath.screen_to_world(
            adjusted_x, adjusted_y, Config.TILE_WIDTH, Config.TILE_HEIGHT
        )
    
    def is_visible(self, world_x: int, world_y: int) -> bool:
        """Check if a world coordinate is visible on screen"""
        screen_x, screen_y = self.world_to_screen(world_x, world_y)
        
        # Add some margin for tiles that are partially visible
        margin = Config.TILE_WIDTH * self.zoom
        
        return (-margin <= screen_x <= self.screen_width + margin and
                -margin <= screen_y <= self.screen_height + margin)
    
    def get_visible_bounds(self) -> tuple:
        """Get the world bounds that are currently visible"""
        # Get corners of screen in world coordinates
        top_left = self.screen_to_world(0, 0)
        top_right = self.screen_to_world(self.screen_width, 0)
        bottom_left = self.screen_to_world(0, self.screen_height)
        bottom_right = self.screen_to_world(self.screen_width, self.screen_height)
        
        # Find bounds
        min_x = min(top_left[0], top_right[0], bottom_left[0], bottom_right[0]) - 1
        max_x = max(top_left[0], top_right[0], bottom_left[0], bottom_right[0]) + 1
        min_y = min(top_left[1], top_right[1], bottom_left[1], bottom_right[1]) - 1
        max_y = max(top_left[1], top_right[1], bottom_left[1], bottom_right[1]) + 1
        
        return min_x, min_y, max_x, max_y
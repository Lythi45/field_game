"""
Main rendering system for the isometric game
"""

import pygame
from typing import Optional
from src.config import Config
from src.graphics.camera import Camera
from src.world.world import World
from src.world.tile import TileType

class Renderer:
    """Handles all rendering operations for the game"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.camera = Camera(screen.get_width(), screen.get_height())
        
        # Create basic tile surfaces (placeholder colored rectangles)
        self.tile_surfaces = self._create_tile_surfaces()
        
        # Font for debug text
        self.debug_font = pygame.font.Font(None, 24)
        
        # Selection
        self.selected_tile = None
    
    def _create_tile_surfaces(self) -> dict:
        """Create colored surfaces for each tile type (placeholder graphics)"""
        surfaces = {}
        
        # Create diamond-shaped isometric tiles
        for tile_type in TileType:
            surface = self._create_isometric_tile(tile_type)
            surfaces[tile_type] = surface
        
        return surfaces
    
    def _create_isometric_tile(self, tile_type: TileType) -> pygame.Surface:
        """Create a diamond-shaped tile surface"""
        width = Config.TILE_WIDTH
        height = Config.TILE_HEIGHT
        
        # Create surface with alpha
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Get tile color
        if tile_type == TileType.GRASS:
            color = (34, 139, 34)
        elif tile_type == TileType.DIRT:
            color = (139, 69, 19)
        elif tile_type == TileType.WATER:
            color = (0, 191, 255)
        elif tile_type == TileType.STONE:
            color = (128, 128, 128)
        elif tile_type == TileType.FARMLAND:
            color = (160, 82, 45)
        elif tile_type == TileType.ROAD:
            color = (105, 105, 105)
        else:
            color = (255, 255, 255)
        
        # Draw diamond shape
        points = [
            (width // 2, 0),           # Top
            (width, height // 2),      # Right
            (width // 2, height),      # Bottom
            (0, height // 2)           # Left
        ]
        
        pygame.draw.polygon(surface, color, points)
        
        # Add border
        pygame.draw.polygon(surface, (0, 0, 0), points, 1)
        
        return surface
    
    def render_world(self, world: World):
        """Render the game world"""
        # Clear screen
        self.screen.fill(Config.BACKGROUND_COLOR)
        
        # Get visible bounds to optimize rendering
        min_x, min_y, max_x, max_y = self.camera.get_visible_bounds()
        
        # Clamp to world bounds
        min_x = max(0, min_x)
        min_y = max(0, min_y)
        max_x = min(world.width - 1, max_x)
        max_y = min(world.height - 1, max_y)
        
        # Render tiles in correct order (back to front for isometric)
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                tile = world.get_tile(x, y)
                if tile:
                    self._render_tile(tile)
        
        # Render selection
        if self.selected_tile:
            self._render_selection(self.selected_tile)
        
        # Render debug info
        if Config.DEBUG_MODE:
            self._render_debug_info()
    
    def _render_tile(self, tile):
        """Render a single tile"""
        # Get screen position
        screen_x, screen_y = self.camera.world_to_screen(tile.x, tile.y)
        
        # Get tile surface
        surface = self.tile_surfaces.get(tile.type)
        if surface:
            # Calculate position (center the tile)
            pos_x = screen_x - Config.TILE_WIDTH // 2
            pos_y = screen_y - Config.TILE_HEIGHT // 2
            
            self.screen.blit(surface, (pos_x, pos_y))
        
        # Render building if present
        if tile.building:
            self._render_building(tile.building, screen_x, screen_y)
        
        # Render crop if present
        if tile.crop:
            self._render_crop(tile.crop, screen_x, screen_y)
    
    def _render_building(self, building, screen_x: int, screen_y: int):
        """Render a building (placeholder)"""
        # Simple colored rectangle for now
        rect = pygame.Rect(
            screen_x - 20, screen_y - 30,
            40, 40
        )
        pygame.draw.rect(self.screen, (139, 69, 19), rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)
    
    def _render_crop(self, crop, screen_x: int, screen_y: int):
        """Render a crop (placeholder)"""
        # Simple green circle for now
        pygame.draw.circle(self.screen, (0, 255, 0), (screen_x, screen_y - 10), 8)
    
    def _render_selection(self, tile):
        """Render selection highlight"""
        screen_x, screen_y = self.camera.world_to_screen(tile.x, tile.y)
        
        # Draw selection diamond
        points = [
            (screen_x, screen_y - Config.TILE_HEIGHT // 2),
            (screen_x + Config.TILE_WIDTH // 2, screen_y),
            (screen_x, screen_y + Config.TILE_HEIGHT // 2),
            (screen_x - Config.TILE_WIDTH // 2, screen_y)
        ]
        
        pygame.draw.polygon(self.screen, Config.SELECTION_COLOR, points, 3)
    
    def _render_debug_info(self):
        """Render debug information"""
        debug_texts = [
            f"Camera: ({self.camera.x:.1f}, {self.camera.y:.1f})",
            f"Zoom: {self.camera.zoom:.2f}",
            f"FPS: {pygame.time.Clock().get_fps():.1f}"
        ]
        
        if self.selected_tile:
            debug_texts.append(f"Selected: ({self.selected_tile.x}, {self.selected_tile.y})")
            debug_texts.append(f"Tile Type: {self.selected_tile.type.value}")
        
        y_offset = 10
        for text in debug_texts:
            surface = self.debug_font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (10, y_offset))
            y_offset += 25
    
    def handle_mouse_click(self, mouse_pos: tuple, world: World):
        """Handle mouse click for tile selection"""
        world_x, world_y = self.camera.screen_to_world(mouse_pos[0], mouse_pos[1])
        
        # Clamp to world bounds
        if 0 <= world_x < world.width and 0 <= world_y < world.height:
            self.selected_tile = world.get_tile(world_x, world_y)
    
    def get_camera(self) -> Camera:
        """Get the camera instance"""
        return self.camera
    
    def set_selected_tile(self, tile):
        """Set the selected tile"""
        self.selected_tile = tile
    
    def get_selected_tile(self):
        """Get the currently selected tile"""
        return self.selected_tile
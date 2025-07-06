"""
Game world management
"""

import random
from typing import List, Optional, Tuple
from src.world.tile import Tile, TileType
from src.config import Config

class World:
    """Manages the game world grid and tiles"""
    
    def __init__(self, width: int = None, height: int = None):
        self.width = width or Config.WORLD_WIDTH
        self.height = height or Config.WORLD_HEIGHT
        
        # 2D grid of tiles
        self.tiles: List[List[Tile]] = []
        
        # Initialize the world
        self._generate_world()
    
    def _generate_world(self):
        """Generate the initial world"""
        self.tiles = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Simple world generation - mostly grass with some variation
                tile_type = self._get_random_tile_type(x, y)
                tile = Tile(tile_type, x, y)
                row.append(tile)
            self.tiles.append(row)
    
    def _get_random_tile_type(self, x: int, y: int) -> TileType:
        """Generate a tile type based on position and randomness"""
        # Simple noise-like generation
        random.seed(x * 1000 + y)  # Deterministic based on position
        
        # Most tiles are grass
        rand = random.random()
        
        if rand < 0.7:
            return TileType.GRASS
        elif rand < 0.85:
            return TileType.DIRT
        elif rand < 0.95:
            return TileType.STONE
        else:
            return TileType.WATER
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at world coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if coordinates are within world bounds"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a position is walkable"""
        tile = self.get_tile(x, y)
        return tile is not None and tile.can_walk()
    
    def is_buildable(self, x: int, y: int) -> bool:
        """Check if a building can be placed at position"""
        tile = self.get_tile(x, y)
        return tile is not None and tile.can_build()
    
    def is_farmable(self, x: int, y: int) -> bool:
        """Check if crops can be planted at position"""
        tile = self.get_tile(x, y)
        return tile is not None and tile.can_farm()
    
    def place_building(self, x: int, y: int, building) -> bool:
        """Place a building at world coordinates"""
        tile = self.get_tile(x, y)
        if tile:
            return tile.place_building(building)
        return False
    
    def remove_building(self, x: int, y: int) -> bool:
        """Remove building at world coordinates"""
        tile = self.get_tile(x, y)
        if tile and tile.building:
            tile.remove_building()
            return True
        return False
    
    def plant_crop(self, x: int, y: int, crop) -> bool:
        """Plant a crop at world coordinates"""
        tile = self.get_tile(x, y)
        if tile:
            return tile.plant_crop(crop)
        return False
    
    def harvest_crop(self, x: int, y: int):
        """Harvest crop at world coordinates"""
        tile = self.get_tile(x, y)
        if tile:
            return tile.harvest_crop()
        return None
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighboring coordinates (4-directional)"""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # N, E, S, W
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_valid_position(nx, ny):
                neighbors.append((nx, ny))
        
        return neighbors
    
    def get_neighbors_8(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighboring coordinates (8-directional)"""
        neighbors = []
        directions = [
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1)
        ]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_valid_position(nx, ny):
                neighbors.append((nx, ny))
        
        return neighbors
    
    def find_nearest_walkable(self, x: int, y: int, max_distance: int = 10) -> Optional[Tuple[int, int]]:
        """Find the nearest walkable tile to given coordinates"""
        if self.is_walkable(x, y):
            return (x, y)
        
        # BFS to find nearest walkable tile
        from collections import deque
        
        queue = deque([(x, y, 0)])
        visited = set()
        
        while queue:
            cx, cy, dist = queue.popleft()
            
            if dist > max_distance:
                break
            
            if (cx, cy) in visited:
                continue
            
            visited.add((cx, cy))
            
            if self.is_walkable(cx, cy):
                return (cx, cy)
            
            # Add neighbors
            for nx, ny in self.get_neighbors(cx, cy):
                if (nx, ny) not in visited:
                    queue.append((nx, ny, dist + 1))
        
        return None
    
    def update(self, dt: float):
        """Update world state (crops growing, etc.)"""
        for row in self.tiles:
            for tile in row:
                if tile.crop:
                    tile.crop.update(dt)
    
    def __str__(self):
        return f"World({self.width}x{self.height})"
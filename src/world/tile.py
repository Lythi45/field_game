"""
Tile system for the game world
"""

from enum import Enum
from typing import Optional

class TileType(Enum):
    """Different types of tiles in the game world"""
    GRASS = "grass"
    DIRT = "dirt"
    WATER = "water"
    STONE = "stone"
    FARMLAND = "farmland"
    ROAD = "road"

class Tile:
    """Represents a single tile in the game world"""
    
    def __init__(self, tile_type: TileType = TileType.GRASS, x: int = 0, y: int = 0):
        self.type = tile_type
        self.x = x
        self.y = y
        
        # Tile properties
        self.walkable = True
        self.buildable = True
        self.farmable = False
        
        # Tile state
        self.occupied = False
        self.building = None
        self.crop = None
        
        # Visual properties
        self.elevation = 0
        self.variant = 0  # For tile variations
        
        self._set_properties()
    
    def _set_properties(self):
        """Set tile properties based on type"""
        if self.type == TileType.GRASS:
            self.walkable = True
            self.buildable = True
            self.farmable = True
        elif self.type == TileType.DIRT:
            self.walkable = True
            self.buildable = True
            self.farmable = True
        elif self.type == TileType.WATER:
            self.walkable = False
            self.buildable = False
            self.farmable = False
        elif self.type == TileType.STONE:
            self.walkable = True
            self.buildable = False
            self.farmable = False
        elif self.type == TileType.FARMLAND:
            self.walkable = True
            self.buildable = False
            self.farmable = True
        elif self.type == TileType.ROAD:
            self.walkable = True
            self.buildable = False
            self.farmable = False
    
    def can_build(self) -> bool:
        """Check if a building can be placed on this tile"""
        return self.buildable and not self.occupied
    
    def can_farm(self) -> bool:
        """Check if crops can be planted on this tile"""
        return self.farmable and not self.occupied and self.crop is None
    
    def can_walk(self) -> bool:
        """Check if characters can walk on this tile"""
        return self.walkable
    
    def place_building(self, building):
        """Place a building on this tile"""
        if self.can_build():
            self.building = building
            self.occupied = True
            return True
        return False
    
    def remove_building(self):
        """Remove building from this tile"""
        self.building = None
        self.occupied = False
    
    def plant_crop(self, crop):
        """Plant a crop on this tile"""
        if self.can_farm():
            self.crop = crop
            # Convert tile to farmland when crop is planted
            if self.type != TileType.FARMLAND:
                self.type = TileType.FARMLAND
                self._set_properties()  # Update properties for farmland
            return True
        return False
    
    def harvest_crop(self):
        """Harvest crop from this tile"""
        if self.crop and self.crop.is_ready():
            harvested_crop = self.crop
            self.crop = None
            return harvested_crop
        return None
    
    def get_color(self) -> tuple:
        """Get the color representation of this tile for debugging"""
        colors = {
            TileType.GRASS: (34, 139, 34),    # Forest green
            TileType.DIRT: (139, 69, 19),     # Saddle brown
            TileType.WATER: (0, 191, 255),    # Deep sky blue
            TileType.STONE: (128, 128, 128),  # Gray
            TileType.FARMLAND: (160, 82, 45), # Saddle brown (darker)
            TileType.ROAD: (105, 105, 105),   # Dim gray
        }
        return colors.get(self.type, (255, 255, 255))
    
    def __str__(self):
        return f"Tile({self.type.value}, {self.x}, {self.y})"
    
    def __repr__(self):
        return self.__str__()
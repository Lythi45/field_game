"""
Crop system for farming mechanics
"""

from enum import Enum
import random

class CropType(Enum):
    """Different types of crops"""
    WHEAT = "wheat"
    CORN = "corn"
    POTATO = "potato"
    CARROT = "carrot"

class GrowthStage(Enum):
    """Growth stages of crops"""
    SEED = 0
    SPROUT = 1
    YOUNG = 2
    MATURE = 3
    READY = 4

class Crop:
    """Represents a growing crop"""
    
    def __init__(self, crop_type: CropType = CropType.WHEAT):
        self.type = crop_type
        self.stage = GrowthStage.SEED
        self.growth_time = 0.0
        self.watered = False
        self.health = 100.0
        
        # Crop properties based on type
        self.properties = self._get_crop_properties()
        
        # Growth timing
        self.stage_duration = self.properties["stage_duration"]
        self.total_growth_time = self.stage_duration * len(GrowthStage)
    
    def _get_crop_properties(self) -> dict:
        """Get properties for this crop type"""
        properties = {
            CropType.WHEAT: {
                "stage_duration": 30.0,  # seconds per stage
                "yield": (2, 4),  # min, max yield
                "value": 10,
                "water_need": 0.8
            },
            CropType.CORN: {
                "stage_duration": 45.0,
                "yield": (1, 3),
                "value": 15,
                "water_need": 1.0
            },
            CropType.POTATO: {
                "stage_duration": 25.0,
                "yield": (3, 6),
                "value": 8,
                "water_need": 0.6
            },
            CropType.CARROT: {
                "stage_duration": 20.0,
                "yield": (2, 5),
                "value": 12,
                "water_need": 0.7
            }
        }
        return properties.get(self.type, properties[CropType.WHEAT])
    
    def update(self, dt: float):
        """Update crop growth"""
        if self.stage == GrowthStage.READY:
            return  # Fully grown
        
        # Growth rate affected by water and health
        growth_rate = 1.0
        if self.watered:
            growth_rate *= 1.2
        growth_rate *= (self.health / 100.0)
        
        self.growth_time += dt * growth_rate
        
        # Check for stage advancement
        current_stage_time = self.growth_time % self.stage_duration
        new_stage_index = min(int(self.growth_time / self.stage_duration), len(GrowthStage) - 1)
        
        if new_stage_index > self.stage.value:
            self.stage = GrowthStage(new_stage_index)
            print(f"Crop advanced to stage: {self.stage.name}")
        
        # Reset watered status (needs daily watering)
        if current_stage_time < dt:  # New day
            self.watered = False
    
    def water(self):
        """Water the crop"""
        self.watered = True
        self.health = min(100.0, self.health + 10.0)
    
    def is_ready(self) -> bool:
        """Check if crop is ready for harvest"""
        return self.stage == GrowthStage.READY
    
    def harvest(self) -> dict:
        """Harvest the crop and return yield"""
        if not self.is_ready():
            return {"type": self.type, "amount": 0, "value": 0}
        
        # Calculate yield
        min_yield, max_yield = self.properties["yield"]
        amount = random.randint(min_yield, max_yield)
        
        # Health affects yield
        amount = int(amount * (self.health / 100.0))
        
        total_value = amount * self.properties["value"]
        
        return {
            "type": self.type,
            "amount": amount,
            "value": total_value
        }
    
    def get_growth_progress(self) -> float:
        """Get growth progress as percentage (0.0 to 1.0)"""
        return min(1.0, self.growth_time / self.total_growth_time)
    
    def __str__(self):
        return f"Crop({self.type.value}, {self.stage.name}, {self.get_growth_progress():.1%})"
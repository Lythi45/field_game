"""
Building system for construction and infrastructure
"""

from enum import Enum
from typing import Dict, List

class BuildingType(Enum):
    """Different types of buildings"""
    HOUSE = "house"
    FARM = "farm"
    WORKSHOP = "workshop"
    WAREHOUSE = "warehouse"
    WELL = "well"
    ROAD = "road"

class BuildingState(Enum):
    """Building construction states"""
    PLANNED = "planned"
    UNDER_CONSTRUCTION = "under_construction"
    COMPLETED = "completed"
    DAMAGED = "damaged"

class Building:
    """Represents a building in the game"""
    
    def __init__(self, building_type: BuildingType, x: int, y: int):
        self.type = building_type
        self.x = x
        self.y = y
        self.state = BuildingState.PLANNED
        
        # Building properties
        self.properties = self._get_building_properties()
        
        # Construction
        self.construction_progress = 0.0
        self.construction_time = self.properties["construction_time"]
        
        # Functionality
        self.capacity = self.properties.get("capacity", 0)
        self.workers_assigned = []
        self.inventory = {}  # For storage buildings, this holds stored items
        self.efficiency = 1.0
        
        # Storage-specific properties
        self.storage_capacity = self.properties.get("storage_capacity", 0)
        self.current_storage = 0
        
        # Maintenance
        self.durability = 100.0
        self.last_maintenance = 0.0
    
    def _get_building_properties(self) -> dict:
        """Get properties for this building type"""
        properties = {
            BuildingType.HOUSE: {
                "construction_time": 60.0,  # seconds
                "cost": {"wood": 10, "stone": 5},
                "capacity": 4,  # max workers
                "function": "housing"
            },
            BuildingType.FARM: {
                "construction_time": 45.0,
                "cost": {"wood": 8, "stone": 2},
                "capacity": 2,
                "function": "farming"
            },
            BuildingType.WORKSHOP: {
                "construction_time": 90.0,
                "cost": {"wood": 15, "stone": 10, "iron": 5},
                "capacity": 3,
                "function": "crafting"
            },
            BuildingType.WAREHOUSE: {
                "construction_time": 75.0,
                "cost": {"wood": 20, "stone": 8},
                "capacity": 1,  # workers that can work here
                "storage_capacity": 1000,  # items that can be stored
                "function": "storage"
            },
            BuildingType.WELL: {
                "construction_time": 30.0,
                "cost": {"stone": 15},
                "capacity": 0,
                "function": "water_source"
            },
            BuildingType.ROAD: {
                "construction_time": 10.0,
                "cost": {"stone": 2},
                "capacity": 0,
                "function": "transport"
            }
        }
        return properties.get(self.type, properties[BuildingType.HOUSE])
    
    def update(self, dt: float):
        """Update building state"""
        if self.state == BuildingState.UNDER_CONSTRUCTION:
            self._update_construction(dt)
        elif self.state == BuildingState.COMPLETED:
            self._update_operation(dt)
            self._update_maintenance(dt)
    
    def _update_construction(self, dt: float):
        """Update construction progress"""
        # Construction speed affected by number of workers
        construction_speed = len(self.workers_assigned) if self.workers_assigned else 0.5
        
        self.construction_progress += (dt / self.construction_time) * construction_speed
        
        if self.construction_progress >= 1.0:
            self.construction_progress = 1.0
            self.state = BuildingState.COMPLETED
            print(f"Building completed: {self.type.value} at ({self.x}, {self.y})")
    
    def _update_operation(self, dt: float):
        """Update building operation"""
        # Different buildings have different operations
        if self.type == BuildingType.FARM:
            self._operate_farm(dt)
        elif self.type == BuildingType.WORKSHOP:
            self._operate_workshop(dt)
        elif self.type == BuildingType.WAREHOUSE:
            self._operate_warehouse(dt)
    
    def _update_maintenance(self, dt: float):
        """Update building maintenance needs"""
        # Buildings slowly degrade over time
        degradation_rate = 0.1  # % per minute
        self.durability -= (degradation_rate / 60.0) * dt
        
        if self.durability <= 0:
            self.state = BuildingState.DAMAGED
            self.efficiency = 0.1  # Very low efficiency when damaged
        elif self.durability < 50:
            self.efficiency = 0.7  # Reduced efficiency
        else:
            self.efficiency = 1.0
    
    def _operate_farm(self, dt: float):
        """Farm-specific operations"""
        # Farms could automatically tend to nearby crops
        pass
    
    def _operate_workshop(self, dt: float):
        """Workshop-specific operations"""
        # Workshops could process raw materials
        pass
    
    def _operate_warehouse(self, dt: float):
        """Warehouse-specific operations"""
        # Warehouses could organize inventory
        pass
    
    def start_construction(self):
        """Start building construction"""
        if self.state == BuildingState.PLANNED:
            self.state = BuildingState.UNDER_CONSTRUCTION
            print(f"Construction started: {self.type.value}")
    
    def assign_worker(self, worker):
        """Assign a worker to this building"""
        if len(self.workers_assigned) < self.capacity:
            self.workers_assigned.append(worker)
            return True
        return False
    
    def remove_worker(self, worker):
        """Remove a worker from this building"""
        if worker in self.workers_assigned:
            self.workers_assigned.remove(worker)
            return True
        return False
    
    def repair(self, amount: float = 50.0):
        """Repair the building"""
        self.durability = min(100.0, self.durability + amount)
        if self.durability > 0 and self.state == BuildingState.DAMAGED:
            self.state = BuildingState.COMPLETED
    
    def get_construction_progress(self) -> float:
        """Get construction progress as percentage"""
        return self.construction_progress
    
    def is_completed(self) -> bool:
        """Check if building is completed"""
        return self.state == BuildingState.COMPLETED
    
    def can_operate(self) -> bool:
        """Check if building can operate"""
        return self.state == BuildingState.COMPLETED and self.durability > 0
    
    def store_item(self, item_type: str, amount: int) -> int:
        """Store items in this building. Returns amount actually stored."""
        if not self.can_operate() or self.properties.get("function") != "storage":
            return 0
        
        # Check storage capacity
        space_available = self.storage_capacity - self.current_storage
        amount_to_store = min(amount, space_available)
        
        if amount_to_store > 0:
            if item_type in self.inventory:
                self.inventory[item_type] += amount_to_store
            else:
                self.inventory[item_type] = amount_to_store
            
            self.current_storage += amount_to_store
            return amount_to_store
        
        return 0
    
    def get_storage_info(self) -> dict:
        """Get storage information for this building"""
        if self.properties.get("function") != "storage":
            return {}
        
        return {
            "inventory": self.inventory.copy(),
            "current_storage": self.current_storage,
            "storage_capacity": self.storage_capacity,
            "space_available": self.storage_capacity - self.current_storage
        }
    
    def __str__(self):
        return f"Building({self.type.value}, {self.state.name}, {self.x}, {self.y})"